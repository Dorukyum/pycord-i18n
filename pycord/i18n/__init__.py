from typing import Dict, Literal, Optional, TypedDict, TypeVar, Union

from discord import ApplicationContext, Bot, ContextMenuCommand, SlashCommand, utils

__all__ = ("Locale", "I18n", "_")

Localizable = Union[SlashCommand, ContextMenuCommand]
CommandT = TypeVar("CommandT", bound=Localizable)
Locale = Literal[
    "da",
    "de",
    "en-GB",
    "en-US",
    "es-ES",
    "fr",
    "hr",
    "it",
    "lt",
    "hu",
    "nl",
    "no",
    "pl",
    "pt-BR",
    "ro",
    "fi",
    "sv-SE",
    "vi",
    "tr",
    "cs",
    "el",
    "bg",
    "ru",
    "uk",
    "hi",
    "th",
    "zh-CN",
    "ja",
    "zh-TW",
    "ko",
]


class Internationalization(TypedDict, total=False):
    strings: Dict[str, str]
    commands: Dict[str, Dict[Literal["name", "description"], str]]


class I18n:
    """A class for internationalization.

    Parameters
    ----------
    bot: discord.Bot
        The pycord bot to add internationalized for.
    consider_user_locale: bool
        Whether to consider the user's locale when translating responses or not.
        By default this is `False` and responses will be based on the server's locale.
    **translations:
        Key-value pairs of locales and translations based on the following format:

        .. code-block:: python

            de={
                "strings": {"Hello!": "Hallo!"},
                "commands": {
                    "help": {
                        "name": "hilfe",
                        "description": "...",
                    }
                }
            }
    """

    instance: "I18n"
    current_locale: Locale

    def __init__(
        self,
        bot: Bot,
        *,
        consider_user_locale: bool = False,
        **internalizations: Internationalization,
    ) -> None:
        self.translations: Dict[Locale, Dict[str, str]] = {  # type: ignore
            k.replace("_", "-"): strings
            for k, v in internalizations.items()
            if (strings := v.get("strings"))
        }
        self.localizations: Dict[Locale, Dict[str, Dict[Literal["name", "description"], str]]] = {  # type: ignore
            k.replace("_", "-"): commands
            for k, v in internalizations.items()
            if (commands := v.get("commands"))
        }
        self.consider_user_locale = consider_user_locale
        self.bot: Bot = bot
        bot.before_invoke(self.set_current_locale)
        I18n.instance = self

    def _localize_command(
        self,
        command: Localizable,
        locale: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> None:
        if name:
            if command.name_localizations is not None:
                command.name_localizations[locale] = name
            else:
                command.name_localizations = {locale: name}
        if isinstance(command, SlashCommand) and description:
            if command.description_localizations is not None:
                command.description_localizations[locale] = description
            else:
                command.description_localizations = {locale: description}

    def localize(self, command: CommandT) -> CommandT:
        """A decorator to apply name and description localizations to a command."""

        for locale, localized in self.localizations.items():
            if localizations := localized.get(command.qualified_name):
                self._localize_command(
                    command,
                    locale,
                    localizations.get("name"),
                    localizations.get("description"),
                )
        return command

    def localize_commands(self) -> None:
        """Localize pending commands. This doesn't update commands on Discord
        and should be ran prior to `bot.sync_commands`."""

        for locale, localized in self.localizations.items():
            for command_name, localizations in localized.items():
                if command := utils.get(
                    self.bot._pending_application_commands, qualified_name=command_name
                ):
                    self._localize_command(
                        command,
                        locale,
                        localizations.get("name"),
                        localizations.get("description"),
                    )

    async def set_current_locale(self, ctx: ApplicationContext) -> None:
        """Sets the locale to be used in the next translation session. This is passed
        to `bot.before_invoke`."""

        if (
            locale := (ctx.locale or ctx.guild_locale)
            if self.consider_user_locale
            else ctx.guild_locale
        ):
            self.current_locale = locale  # type: ignore # locale is of type Locale

    @classmethod
    def get_text(cls, original: str) -> str:
        """Translate a string based on the `translations` attribute of the i18n object.
        Returns the passed string if a translation for the current locale isn't found."""

        self = I18n.instance
        if (translations := self.translations.get(self.current_locale)) and (
            translation := translations.get(original)
        ):
            return translation
        return original


_ = I18n.get_text
