from constants.google_play_constants import MAX_GOOGLE_PLAY_TITLE_LENGTH, MAX_GOOGLE_PLAY_SHORT_DESCRIPTION_LENGTH, \
    MAX_GOOGLE_PLAY_FULL_DESCRIPTION_LENGTH

MCP_SERVER_INSTRUCTIONS = f"""
This server provides tools to perform ASO research in Google Play Store.

## Languages and countries

Each request should be sent for the given language and country.
Please note that Google Play Store's languages and countries codes might be different from the "usual" ones.

- Call `get-google-play-languages()` to get list of available language codes.
- Call `get-google-play-countries()` to get list of available country codes.
- Call `get-google-play-countries-with-languages()` to get list of available country codes mapped with languages codes that are used in these countries

## Keywords research

Call `google-play-suggest()` to get keywords suggestions for the given keyword.

You will need to pass some "seed" keyword (or a part of it) to get suggestions - empty `keyword` will not work.

For example, you're calling it with:

- `country`: `ru`
- `language`: `ru`
- `keyword`: `каль` - see, this is not a full keyword, but only a part of it

In this case, it will return something like this:

```
{{
"result": [
    "калькулятор",
    "калькулятор имт",
    "калькулятор дробей",
    "калькулятор калорий",
    "калькулятор в столбик"
  ]
}}
```

## Data validation

When you're generating metadata for Google Play Store, you can validate it using these methods:

- Call `google-play-validate-title()` to validate title
- Call `google-play-validate-short-description()` to validate short description
- Call `google-play-validate-full-description()` to validate full description

Current limitations for metadata on Google Play Store:

- {MAX_GOOGLE_PLAY_TITLE_LENGTH} characters for title
- {MAX_GOOGLE_PLAY_SHORT_DESCRIPTION_LENGTH} characters for short description
- {MAX_GOOGLE_PLAY_FULL_DESCRIPTION_LENGTH} characters for full description
"""
