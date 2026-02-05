from constants.google_play_constants import MAX_GOOGLE_PLAY_TITLE_LENGTH, MAX_GOOGLE_PLAY_SHORT_DESCRIPTION_LENGTH, \
    MAX_GOOGLE_PLAY_FULL_DESCRIPTION_LENGTH

MCP_SERVER_INSTRUCTIONS = f"""
This server provides tools for App Store Optimization (ASO) research in Google Play Store.

## Reference Data

**Localization:**
- `get-google-play-languages()` - available language codes
- `get-google-play-countries()` - available country codes
- `get-google-play-countries-with-languages()` - country codes with their supported languages

**Enums for API calls:**
- `get-google-play-collections()` - collection types: TOP_FREE, TOP_PAID, GROSSING
- `get-google-play-categories()` - app categories: APPLICATION, GAME, GAME_ACTION, etc.
- `get-google-play-sort-orders()` - review sort orders: NEWEST, RATING, HELPFULNESS
- `get-google-play-age-filters()` - age filters: FIVE_UNDER, SIX_EIGHT, NINE_UP
- `get-google-play-rating-filters()` - rating filters: 1-5

## App Discovery

- `google-play-search(country, language, term, num?, price?)` - search apps by keyword
  - `price`: "all", "free", or "paid"
- `google-play-list(country, language, collection, category, num?, age?)` - browse collections
- `google-play-app(country, language, app_id)` - get detailed app info
- `google-play-reviews(country, language, app_id, sort?, num?, filter_rating?, continuation_token?)` - get reviews with pagination

## Keywords Research

- `google-play-suggest(country, language, keyword)` - get keyword suggestions

Pass a partial or a full keyword to get autocomplete suggestions. Example: "calc" → ["calculator", "calculator pro", ...]

## Metadata Validation

- `google-play-validate-title(title)` - max {MAX_GOOGLE_PLAY_TITLE_LENGTH} chars
- `google-play-validate-short-description(short_description)` - max {MAX_GOOGLE_PLAY_SHORT_DESCRIPTION_LENGTH} chars
- `google-play-validate-full-description(full_description)` - max {MAX_GOOGLE_PLAY_FULL_DESCRIPTION_LENGTH} chars
"""
