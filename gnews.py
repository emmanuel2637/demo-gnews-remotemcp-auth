"""
MCP Server for Gnews API - Integrating search and top headlines endpoints
Run from the repository root:
    uv run main.py
"""

import os
from typing import Any

import requests
from pydantic import BaseModel, Field

from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP(
    "Gnews Server",
    instructions="Access news articles through Gnews API - search for specific topics or get trending headlines",
    json_response=True
)

# Gnews API configuration
GNEWS_API_BASE = "https://gnews.io/api/v4"
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY", "")

# Supported languages for search endpoint
SEARCH_LANGUAGES = {
    "ar": "Arabic", "bn": "Bengali", "zh": "Chinese", "nl": "Dutch",
    "en": "English", "fr": "French", "de": "German", "el": "Greek",
    "he": "Hebrew", "hi": "Hindi", "id": "Indonesian", "it": "Italian",
    "ja": "Japanese", "ml": "Malayalam", "mr": "Marathi", "no": "Norwegian",
    "pt": "Portuguese", "pa": "Punjabi", "ro": "Romanian", "ru": "Russian",
    "es": "Spanish", "sv": "Swedish", "ta": "Tamil", "te": "Telugu",
    "tr": "Turkish", "uk": "Ukrainian"
}

# Supported languages for top headlines (includes more than search)
HEADLINES_LANGUAGES = {
    **SEARCH_LANGUAGES,
    "bg": "Bulgarian", "ca": "Catalan", "cs": "Czech", "et": "Estonian",
    "fi": "Finnish", "gu": "Gujarati", "hu": "Hungarian", "ko": "Korean",
    "lv": "Latvian", "lt": "Lithuanian", "pl": "Polish", "sk": "Slovak",
    "sl": "Slovenian", "th": "Thai", "vi": "Vietnamese"
}

# Supported countries
COUNTRIES = {
    "ar": "Argentina", "at": "Austria", "au": "Australia", "bd": "Bangladesh",
    "be": "Belgium", "bw": "Botswana", "br": "Brazil", "bg": "Bulgaria",
    "ca": "Canada", "cl": "Chile", "cn": "China", "co": "Colombia",
    "cu": "Cuba", "cz": "Czechia", "eg": "Egypt", "ee": "Estonia",
    "et": "Ethiopia", "fi": "Finland", "fr": "France", "de": "Germany",
    "gh": "Ghana", "gr": "Greece", "hk": "Hong Kong", "hu": "Hungary",
    "in": "India", "id": "Indonesia", "ie": "Ireland", "il": "Israel",
    "it": "Italy", "jp": "Japan", "ke": "Kenya", "lv": "Latvia",
    "lb": "Lebanon", "lt": "Lithuania", "my": "Malaysia", "mx": "Mexico",
    "ma": "Morocco", "na": "Namibia", "nl": "Netherlands", "nz": "New Zealand",
    "ng": "Nigeria", "no": "Norway", "pk": "Pakistan", "pe": "Peru",
    "ph": "Philippines", "pl": "Poland", "pt": "Portugal", "ro": "Romania",
    "ru": "Russia", "sa": "Saudi Arabia", "sn": "Senegal", "sg": "Singapore",
    "sk": "Slovakia", "si": "Slovenia", "za": "South Africa", "kr": "South Korea",
    "es": "Spain", "se": "Sweden", "ch": "Switzerland", "tw": "Taiwan",
    "tz": "Tanzania", "th": "Thailand", "tr": "Turkey", "ug": "Uganda",
    "ua": "Ukraine", "ae": "United Arab Emirates", "gb": "United Kingdom",
    "us": "United States", "ve": "Venezuela", "vn": "Vietnam", "zw": "Zimbabwe"
}

# Top headlines categories
HEADLINES_CATEGORIES = [
    "general", "world", "nation", "business", "technology",
    "entertainment", "sports", "science", "health"
]


class Article(BaseModel):
    """Represents a news article from Gnews API"""
    title: str = Field(description="Article title")
    description: str | None = Field(description="Article description")
    content: str | None = Field(description="Full article content")
    url: str = Field(description="URL to the article")
    image: str | None = Field(description="Image URL")
    source: dict[str, Any] = Field(description="Source information")
    publishedAt: str = Field(description="Publication timestamp")


class SearchResult(BaseModel):
    """Result from search endpoint"""
    totalArticles: int = Field(description="Total articles found")
    articles: list[Article] = Field(description="List of articles")


@mcp.tool()
def search_news(
    q: str,
    lang: str | None = None,
    country: str | None = None,
    max: int = 10,
    in_fields: str = "title,description",
    sortby: str = "publishedAt",
    page: int = 1
) -> SearchResult:
    """
    Search for news articles using keywords.
    
    Args:
        q: Search keywords (required, max 200 characters). Supports logical operators: AND, OR, NOT
        lang: Language code (e.g., 'en' for English). See supported languages.
        country: Country code (e.g., 'us' for United States). See supported countries.
        max: Number of articles to return (1-100, default 10)
        in_fields: Fields to search in - 'title', 'description', 'content' (comma-separated)
        sortby: Sort by 'publishedAt' (default) or 'relevance'
        page: Page number for pagination (default 1)
    
    Returns:
        SearchResult with articles matching the search query
    
    Examples:
        - search_news("Apple iPhone") - Exact phrase search
        - search_news("Apple OR Microsoft") - Articles about either
        - search_news("Apple AND NOT iPhone") - Apple news excluding iPhone
    """
    if not GNEWS_API_KEY:
        raise ValueError("GNEWS_API_KEY environment variable not set")
    
    if not q or len(q) > 200:
        raise ValueError("Query must be between 1 and 200 characters")
    
    if max < 1 or max > 100:
        raise ValueError("max must be between 1 and 100")
    
    params = {
        "q": q,
        "apikey": GNEWS_API_KEY,
        "max": max,
        "in": in_fields,
        "sortby": sortby,
        "page": page
    }
    
    if lang:
        if lang not in SEARCH_LANGUAGES:
            raise ValueError(f"Language '{lang}' not supported. Supported: {', '.join(SEARCH_LANGUAGES.keys())}")
        params["lang"] = lang
    
    if country:
        if country not in COUNTRIES:
            raise ValueError(f"Country '{country}' not supported. Supported: {', '.join(COUNTRIES.keys())}")
        params["country"] = country
    
    try:
        response = requests.get(f"{GNEWS_API_BASE}/search", params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        return SearchResult(
            totalArticles=data.get("totalArticles", 0),
            articles=[Article(**article) for article in data.get("articles", [])]
        )
    except requests.RequestException as e:
        raise RuntimeError(f"Gnews API error: {str(e)}")


@mcp.tool()
def get_top_headlines(
    category: str = "general",
    lang: str | None = None,
    country: str | None = None,
    max: int = 10,
    q: str | None = None,
    page: int = 1
) -> SearchResult:
    """
    Get top trending headlines from Gnews ranked by popularity.
    
    Args:
        category: News category (default 'general'). 
                 Options: general, world, nation, business, technology, 
                         entertainment, sports, science, health
        lang: Language code (e.g., 'en' for English). See supported languages.
        country: Country code (e.g., 'us' for United States). See supported countries.
        max: Number of articles to return (1-100, default 10)
        q: Optional search keywords within the category
        page: Page number for pagination (default 1)
    
    Returns:
        SearchResult with top headline articles
    
    Examples:
        - get_top_headlines() - General top headlines
        - get_top_headlines(category="technology", country="us") - Tech headlines in US
        - get_top_headlines(category="sports", lang="es", country="mx") - Sports from Mexico in Spanish
    """
    if not GNEWS_API_KEY:
        raise ValueError("GNEWS_API_KEY environment variable not set")
    
    if category not in HEADLINES_CATEGORIES:
        raise ValueError(f"Category '{category}' not valid. Options: {', '.join(HEADLINES_CATEGORIES)}")
    
    if max < 1 or max > 100:
        raise ValueError("max must be between 1 and 100")
    
    params = {
        "category": category,
        "apikey": GNEWS_API_KEY,
        "max": max,
        "page": page
    }
    
    if lang:
        if lang not in HEADLINES_LANGUAGES:
            raise ValueError(f"Language '{lang}' not supported. Supported: {', '.join(HEADLINES_LANGUAGES.keys())}")
        params["lang"] = lang
    
    if country:
        if country not in COUNTRIES:
            raise ValueError(f"Country '{country}' not supported. Supported: {', '.join(COUNTRIES.keys())}")
        params["country"] = country
    
    if q:
        if len(q) > 200:
            raise ValueError("Query must not exceed 200 characters")
        params["q"] = q
    
    try:
        response = requests.get(f"{GNEWS_API_BASE}/top-headlines", params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        return SearchResult(
            totalArticles=data.get("totalArticles", 0),
            articles=[Article(**article) for article in data.get("articles", [])]
        )
    except requests.RequestException as e:
        raise RuntimeError(f"Gnews API error: {str(e)}")




