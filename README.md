<div align="center">
    <h1>pycord-i18n</h1>
    <h2>Internationalization for Pycord</h2>
</div>

## Key Features
- Translated responses
- Command name & description localization
- Based on user & server locale (no need for storage!)

## Usage
1. Setup your internationalization files just like [sample-german.json](https://github.com/Dorukyum/pycord-i18n/blob/main/sample-german.json).

2. Load your files:
```py
import json

with open("sample-german.json", "r") as f:
    german = json.load(f)
...
```

3. Create an I18n object:
```py
from pycord.i18n import I18n, _

i18n = I18n(bot, de=german)
# de is the locale code for German
# response translations will be based on the guild's locale, you can make the bot consider the user's locale too by using the following:
i18n = I18n(bot, consider_user_locale=True, de=german)

# all valid locales: da, de, en_GB, en_US, es_ES, fr, hr, it, lt, hu, nl, no, pl, pt_BR, ro, fi, sv_SE, vi, tr, cs, el, bg, ru, uk, hi, th, zh_CN, ja, zh_TW, ko
```

4. Internationalize your commands:
```py
@i18n.localize  # command name and description localization
@bot.slash_command()
async def hello(ctx):
    await ctx.respond(_("Hello, this sentence is in English"))
    # "_()" does the translation

# if you don't want to use `@localize` on every command, simply use the following method after adding the commands to the bot:
i18n.localize_commands()
```
