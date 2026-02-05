# ASO MCP Server

A Model Context Protocol (MCP) server for App Store Optimization (ASO) research in Google Play Store.

**Please note:** This MCP is a very early feature-limited prototype and is not yet ready for production use.

Built on top of [google-play-scraper](https://github.com/RankoR/google-play-scraper) - a Python library for scraping
Google Play Store data.

## Features

- **App Search** - Search for apps by keyword with price filtering
- **App Details** - Get comprehensive information about any app
- **App Reviews** - Fetch user reviews with sorting, filtering, and pagination
- **Collections & Categories** - Browse top free, top paid, and grossing apps by category
- **Keywords Research** - Get keyword suggestions from Google Play Store autocomplete
- **Metadata Validation** - Validate titles, short descriptions, and full descriptions against Google Play limits
- **Country & Language Support** - Access all Google Play supported countries and languages
- **Proxy Rotation** - Optional proxy support with automatic rotation and retry on failure

## Installation

### Prerequisites

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd aso-mcp-python

# Install dependencies with uv
uv sync

# Or with pip
pip install -e .

# Install development dependencies (for testing)
uv sync --dev
# Or with pip
pip install -e ".[dev]"
```

## Usage

### Running the Server

```bash
uv run python server.py
```

### Integration with AI Assistants

#### Claude Code

Add to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "aso": {
      "command": "uv",
      "args": [
        "run",
        "python",
        "server.py"
      ],
      "cwd": "/path/to/aso-mcp-python"
    }
  }
}
```

#### Gemini CLI

Add to `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "aso": {
      "command": "uv",
      "args": [
        "run",
        "python",
        "server.py"
      ],
      "cwd": "/path/to/aso-mcp-python"
    }
  }
}
```

## Available Tools

### App Search & Discovery

#### `google-play-search`

Search for apps in Google Play Store by keyword.

**Parameters:**

- `country` (string) - Country code (e.g., `us`, `de`, `jp`)
- `language` (string) - Language code (e.g., `en`, `de`, `ja`)
- `term` (string) - Search term
- `num` (integer, optional) - Number of results (default: 20)
- `price` (string, optional) - Price filter: "all", "free", or "paid" (default: "all")

**Returns:** List of app overviews with basic info (title, developer, score, etc.)

#### `google-play-list`

Browse Google Play Store collections and categories.

**Parameters:**

- `country` (string) - Country code
- `language` (string) - Language code
- `collection` (string) - Collection type: "TOP_FREE", "TOP_PAID", or "GROSSING"
- `category` (string) - Category (e.g., "APPLICATION", "GAME_ACTION", "PRODUCTIVITY")
- `num` (integer, optional) - Number of results (default: 50)
- `age` (string, optional) - Age filter: "AGE_RANGE1" (5 and under), "AGE_RANGE2" (6-8), or "AGE_RANGE3" (9+)

**Available Categories:**
- General: `APPLICATION`, `GAME`, `FAMILY`
- App Categories: `BUSINESS`, `EDUCATION`, `ENTERTAINMENT`, `FINANCE`, `HEALTH_AND_FITNESS`, `PRODUCTIVITY`, `TOOLS`, and more
- Game Categories: `GAME_ACTION`, `GAME_ADVENTURE`, `GAME_PUZZLE`, `GAME_RACING`, `GAME_STRATEGY`, and more

**Returns:** List of app overviews

#### `google-play-app`

Get comprehensive details about a specific app.

**Parameters:**

- `country` (string) - Country code
- `language` (string) - Language code
- `app_id` (string) - App package ID (e.g., "com.spotify.music")

**Returns:** Detailed app information including:
- Basic info (title, developer, summary, descriptions)
- Ratings (score, reviews count, histogram)
- Pricing (price, currency, in-app purchases)
- Install statistics (installs, min/max installs)
- Media (icon, screenshots, video, header image)
- Technical details (version, Android version, release/update dates)
- Contact info (email, website, address)
- Legal (content rating, privacy policy)

#### `google-play-reviews`

Get user reviews for a specific app with pagination support.

**Parameters:**

- `country` (string) - Country code
- `language` (string) - Language code
- `app_id` (string) - App package ID
- `sort` (string, optional) - Sort order: "newest", "rating", or "helpfulness" (default: "newest")
- `num` (integer, optional) - Number of reviews (default: 100)
- `filter_rating` (integer, optional) - Filter by rating (1-5)
- `continuation_token` (string, optional) - Token for fetching next page

**Returns:** Reviews with user info, rating, text, developer reply (if any), and pagination token for next page

### Keywords Research

#### `google-play-suggest`

Get keyword suggestions for a given seed keyword.

**Parameters:**

- `country` (string) - Country code (e.g., `us`, `de`, `jp`)
- `language` (string) - Language code (e.g., `en`, `de`, `ja`)
- `keyword` (string) - Seed keyword or partial keyword

**Example:**

```
country: "us"
language: "en"
keyword: "calc"
```

**Returns:** List of suggested keywords like `["calculator", "calculator app", "calculator free", ...]`

### Metadata Validation

#### `google-play-validate-title`

Validate a title against Google Play's 30 character limit.

**Parameters:**

- `title` (string) - Title to validate

#### `google-play-validate-short-description`

Validate a short description against Google Play's 80 character limit.

**Parameters:**

- `short_description` (string) - Short description to validate

#### `google-play-validate-full-description`

Validate a full description against Google Play's 4000 character limit.

**Parameters:**

- `full_description` (string) - Full description to validate

**Returns:** Validation result with length, validity status, and any errors.

### Reference Data

#### `get-google-play-languages`

Get all language codes supported by Google Play.

#### `get-google-play-countries`

Get all country codes supported by Google Play.

#### `get-google-play-countries-with-languages`

Get country codes mapped to their supported languages.

## Proxy Configuration

The server supports optional proxy rotation for requests to Google Play. This is useful for:

- Avoiding rate limiting
- Geographic distribution of requests
- IP rotation

### Setup

Set the `ASO_MCP_PROXIES` environment variable with a comma-separated list of proxy URLs:

```bash
export ASO_MCP_PROXIES="http://proxy1:8080,http://proxy2:8080,http://user:pass@proxy3:8080"
```

### With Claude Code

```json
{
  "mcpServers": {
    "aso": {
      "command": "uv",
      "args": [
        "run",
        "python",
        "server.py"
      ],
      "cwd": "/path/to/aso-mcp-python",
      "env": {
        "ASO_MCP_PROXIES": "http://proxy1:8080,http://proxy2:8080"
      }
    }
  }
}
```

### With Gemini CLI

```json
{
  "mcpServers": {
    "aso": {
      "command": "uv",
      "args": [
        "run",
        "python",
        "server.py"
      ],
      "cwd": "/path/to/aso-mcp-python",
      "env": {
        "ASO_MCP_PROXIES": "http://proxy1:8080,http://proxy2:8080"
      }
    }
  }
}
```

### How Proxy Rotation Works

1. On each request, a random proxy is selected from the pool
2. If a request fails, the proxy is marked as failed and a different proxy is tried
3. Failed proxies are avoided until all proxies have failed
4. When all proxies fail, the failed list resets and rotation starts over
5. Credentials in proxy URLs are masked in logs for security

### Supported Proxy Formats

```
http://host:port
http://username:password@host:port
https://host:port
https://username:password@host:port
```

## Google Play Metadata Limits

| Field             | Character Limit |
|-------------------|-----------------|
| Title             | 30              |
| Short Description | 80              |
| Full Description  | 4000            |

## Supported Countries

The server supports 60+ countries including:

| Region       | Countries                            |
|--------------|--------------------------------------|
| Americas     | US, CA, BR, MX                       |
| Europe       | GB, DE, FR, ES, IT, NL, PL, and more |
| Asia Pacific | JP, KR, CN, IN, AU, SG, and more     |
| Middle East  | SA, IL, TR, and more                 |

Use `get-google-play-countries-with-languages` to get the full mapping of countries to their supported languages.

## Development

### Project Structure

```
aso-mcp-python/
├── server.py                 # Main MCP server
├── proxy.py                  # Proxy rotation manager
├── constants/
│   ├── google_play_constants.py  # Countries, languages, limits, enums
│   └── mcp_constants.py          # Server instructions
├── models/
│   ├── google_play.py        # Data models (AppDetails, AppOverview, Review)
│   └── metadata.py           # Validation models
├── tests/
│   └── test_server.py        # Comprehensive test suite
├── pyproject.toml            # Project configuration
├── pytest.ini                # Pytest configuration
└── README.md
```

### Dependencies

- `mcp[cli]` - Model Context Protocol SDK
- `play-store-scraper-ng` - Google Play Store scraper
- `httpx` - HTTP client

### Development Dependencies

- `pytest` - Testing framework
- `pytest-asyncio` - Async test support
- `pytest-mock` - Mocking support

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=. --cov-report=html

# Run specific test file
uv run pytest tests/test_server.py

# Run specific test
uv run pytest tests/test_server.py::TestSearch::test_google_play_search_success

# Run with verbose output
uv run pytest -v
```

The test suite includes:
- Unit tests for all tools
- Mock-based tests (no actual API calls)
- Proxy rotation and failure scenarios
- Input validation tests
- Pagination tests for reviews

## License

MIT
