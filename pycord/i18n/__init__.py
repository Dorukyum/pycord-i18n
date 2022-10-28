from typing import Dict, Literal, TypedDict, TypeVar, Union

from discord import ApplicationContext, Bot, ContextMenuCommand, SlashCommand, utils

__all__ = (
    "Locale",
    "OptionLocalization",
    "CommandLocalization",
    "Internationalization",
    "I18n",
    "_",
)

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


class OptionLocalization(TypedDict, total=False):
    name: str
    description: str


class CommandLocalization(OptionLocalization, total=False):
    options: Dict[str, OptionLocalization]


class Internationalization(TypedDict, total=False):
    strings: Dict[str, str]
    commands: Dict[str, CommandLocalization]


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
        Key-value pairs of locales and translations based on the `Internationalization` typeddict.

        .. code-block:: python

            de={
                "strings": {"Hello!": "Hallo!"},
                "commands": {
                    "help": {
                        "name": "hilfe",
                        "description": "...",
                        "options": {
                            "category": {
                                "name": "kategorie",
                                "description": "...",
                            }
                        }
                    }
                }
            }

    Attributes
    ----------
    instance: I18n
        The initialized I18n instance.
    current_locale: Locale
        The locale of the last invokation.
    translations: Dict[Locale, Dict[str, str]]
        String translations. Accessed via `I18n.get_text`.
    localizations: Dict[Locale, Dict[str, CommandLocalization]]
        Command localizations. Applied via `.localize` or `.localize_commands`.
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
        self.localizations: Dict[Locale, Dict[str, CommandLocalization]] = {  # type: ignore
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
        localizations: CommandLocalization,
    ) -> None:
        if name := localizations.get("name"):
            if command.name_localizations is None:
                command.name_localizations = {locale: name}
            else:
                command.name_localizations[locale] = name
        if isinstance(command, SlashCommand):
            if description := localizations.get("description"):
                if command.description_localizations is None:
                    command.description_localizations = {locale: description}
                else:
                    command.description_localizations[locale] = description
            if options := localizations.get("options"):
                for option_name, localization in options.items():
                    if option := utils.get(command.options, name=option_name):
                        if op_name := localization.get("name"):
                            if option.name_localizations is None:
                                option.name_localizations = {locale: op_name}
                            else:
                                option.name_localizations[locale] = op_name
                        if op_description := localization.get("description"):
                            if option.description_localizations is None:
                                option.description_localizations = {
                                    locale: op_description
                                }
                            else:
                                option.description_localizations[
                                    locale
                                ] = op_description

    def localize(self, command: CommandT) -> CommandT:
        """A decorator to apply name and description localizations to a command."""

        for locale, localized in self.localizations.items():
            if localizations := localized.get(command.qualified_name):
                self._localize_command(
                    command,
                    locale,
                    localizations,
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
                        localizations,
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
    def get_text(cls, original: str, *format_args: object) -> str:
        """Translate a string based on the `translations` attribute of the I18n instance.
        Returns the passed string if a translation for the current locale isn't found.
        If `format_args` is given, the output string will be formatted using `text.format(*format_args)`."""

        self = I18n.instance
        text = (
            translation
            if (translations := self.translations.get(self.current_locale))
            and (translation := translations.get(original))
            else original
        )
        if format_args:
            return text.format(*format_args)
        return text


_ = I18n.get_text
