# Gnews MCP Server

A Model Context Protocol (MCP) server that integrates the Gnews API, providing access to news articles through two powerful endpoints.

## Features

This MCP server exposes two main tools:

- **`search_news`** - Search for news articles by keywords with advanced query syntax support
- **`get_top_headlines`** - Get trending articles by category, language, and country

## Prerequisites

- Python 3.12+
- Gnews API key (get one at [https://gnews.io](https://gnews.io))
- UV package manager (optional but recommended)

## Setup

### 1. Install Dependencies

```bash
uv sync
```

Or with pip:

```bash
pip install -r requirements.txt
```

### 2. Set API Key

Set your Gnews API key as an environment variable:

```bash
# On Windows (PowerShell)
$env:GNEWS_API_KEY = "your-api-key-here"

# On Linux/Mac
export GNEWS_API_KEY="your-api-key-here"
```

## Usage

### Running the Server

```bash
uv run main.py
```

The server will start with Streamable HTTP transport on `http://localhost:8000/mcp`.

### Tools

#### Search News

Search for news articles using keywords with support for logical operators.

**Parameters:**
- `q` (required): Search keywords (max 200 chars). Supports AND, OR, NOT operators
- `lang` (optional): Language code (e.g., 'en', 'es', 'fr')
- `country` (optional): Country code (e.g., 'us', 'uk', 'mx')
- `max` (optional): Number of results 1-100 (default: 10)
- `in_fields` (optional): Search fields - 'title', 'description', 'content' (default: 'title,description')
- `sortby` (optional): Sort by 'publishedAt' or 'relevance' (default: 'publishedAt')
- `page` (optional): Page number for pagination (default: 1)

**Examples:**
```
search_news(q="Apple iPhone")                    # Exact phrase
search_news(q="Apple OR Microsoft")              # Either topic
search_news(q="Apple AND NOT iPhone")            # Apple excluding iPhone
search_news(q="technology", lang="en", country="us", max=20)  # Tech news from US
```

#### Get Top Headlines

Get trending news articles by category.

**Parameters:**
- `category` (optional): News category (default: 'general')
  - Options: general, world, nation, business, technology, entertainment, sports, science, health
- `lang` (optional): Language code
- `country` (optional): Country code
- `max` (optional): Number of results 1-100 (default: 10)
- `q` (optional): Additional keyword filter within category
- `page` (optional): Page number for pagination (default: 1)

**Examples:**
```
get_top_headlines()                              # General top headlines
get_top_headlines(category="technology")         # Top tech news
get_top_headlines(category="sports", country="us", lang="en")  # US sports
get_top_headlines(category="business", q="Tesla")  # Business news about Tesla
```

## Supported Languages

**Search Endpoint:** ar, bn, zh, nl, en, fr, de, el, he, hi, id, it, ja, ml, mr, no, pt, pa, ro, ru, es, sv, ta, te, tr, uk

**Top Headlines:** Plus: bg, ca, cs, et, fi, gu, hu, ko, lv, lt, pl, sk, sl, th, vi

## Supported Countries

ar, at, au, bd, be, bw, br, bg, ca, cl, cn, co, cu, cz, eg, ee, et, fi, fr, de, gh, gr, hk, hu, in, id, ie, il, it, jp, ke, lv, lb, lt, my, mx, ma, na, nl, nz, ng, no, pk, pe, ph, pl, pt, ro, ru, sa, sn, sg, sk, si, za, kr, es, se, ch, tw, tz, th, tr, ug, ua, ae, gb, us, ve, vn, zw

## Connecting with Claude Code

After starting the server, you can connect it to Claude Code:

```bash
claude mcp add --transport http gnews-server http://localhost:8000/mcp
```

## Using with MCP Inspector

Test your server with the MCP Inspector:

1. Start the server:
   ```bash
   uv run main.py
   ```

2. In another terminal, run the inspector:
   ```bash
   npx -y @modelcontextprotocol/inspector
   ```

3. Navigate to `http://localhost:8000/mcp` in the inspector UI

## Response Format

Both tools return `SearchResult` objects containing:

```json
{
  "totalArticles": 150,
  "articles": [
    {
      "title": "Article Title",
      "description": "Article description",
      "content": "Full article content",
      "url": "https://...",
      "image": "https://...",
      "source": {
        "name": "Source Name",
        "url": "https://..."
      },
      "publishedAt": "2025-02-25T10:30:00Z"
    }
  ]
}
```

## Error Handling

The server handles various errors:
- Missing API key → "GNEWS_API_KEY environment variable not set"
- Invalid parameters → Descriptive validation errors
- API rate limits → Errors propagated from Gnews API
- Network issues → Timeout and connection errors

## Architecture

The server is built using:
- **FastMCP**: High-level interface from the Python MCP SDK
- **Pydantic**: Data validation and serialization
- **Requests**: HTTP client for API calls

## API Documentation

For more details on the Gnews API, visit:
- [Gnews Search Endpoint](https://docs.gnews.io/endpoints/search-endpoint)
- [Gnews Top Headlines Endpoint](https://docs.gnews.io/endpoints/top-headlines-endpoint)

## MCP Documentation

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Python SDK Documentation](https://modelcontextprotocol.github.io/python-sdk/)

## License

MIT
