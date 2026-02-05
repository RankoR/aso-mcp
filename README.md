# ASO MCP Server

A Model Context Protocol (MCP) server for App Store Optimization (ASO) research in Google Play Store.

**Please note:** This MCP is a very early feature-limited prototype and is not yet ready for production use.

## Features

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
      "args": ["run", "python", "server.py"],
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
      "args": ["run", "python", "server.py"],
      "cwd": "/path/to/aso-mcp-python"
    }
  }
}
```

## Available Tools

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
      "args": ["run", "python", "server.py"],
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
      "args": ["run", "python", "server.py"],
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

| Field | Character Limit |
|-------|----------------|
| Title | 30 |
| Short Description | 80 |
| Full Description | 4000 |

## Supported Countries

The server supports 60+ countries including:

| Region | Countries |
|--------|-----------|
| Americas | US, CA, BR, MX |
| Europe | GB, DE, FR, ES, IT, NL, PL, and more |
| Asia Pacific | JP, KR, CN, IN, AU, SG, and more |
| Middle East | SA, IL, TR, and more |

Use `get-google-play-countries-with-languages` to get the full mapping of countries to their supported languages.

## Development

### Project Structure

```
aso-mcp-python/
├── server.py                 # Main MCP server
├── proxy.py                  # Proxy rotation manager
├── constants/
│   ├── google_play_constants.py  # Countries, languages, limits
│   └── mcp_constants.py          # Server instructions
├── models/
│   ├── google_play.py        # Data models
│   └── metadata.py           # Validation models
├── pyproject.toml            # Project configuration
└── README.md
```

### Dependencies

- `mcp[cli]` - Model Context Protocol SDK
- `play-store-scraper-ng` - Google Play Store scraper
- `httpx` - HTTP client

## License

MIT
