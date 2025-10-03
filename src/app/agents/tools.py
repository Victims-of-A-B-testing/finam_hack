"""
Tools for LangGraph agents to interact with Finam API
"""

from difflib import SequenceMatcher
from typing import Any

from langchain_core.tools import tool

from ..adapters.finam_client import FinamAPIClient

# Initialize the Finam API client
_finam_client: FinamAPIClient | None = None


def get_finam_client() -> FinamAPIClient:
    """Get or create the Finam API client singleton."""
    global _finam_client
    if _finam_client is None:
        _finam_client = FinamAPIClient()
    return _finam_client


def fuzzy_search_assets(query: str, assets: list[dict[str, Any]], limit: int = 5) -> list[dict[str, Any]]:
    """
    Perform fuzzy search on assets list.

    Args:
        query: Search query (company name or ticker)
        assets: List of asset dictionaries from API
        limit: Maximum number of results to return

    Returns:
        List of most similar assets sorted by similarity score
    """
    query_lower = query.lower()
    scored_assets = []

    for asset in assets:
        # Calculate similarity scores for different fields
        name = asset.get("name", "").lower()
        ticker = asset.get("ticker", "").lower()
        symbol = asset.get("symbol", "").lower()

        # Calculate similarity ratios
        name_score = SequenceMatcher(None, query_lower, name).ratio()
        ticker_score = SequenceMatcher(None, query_lower, ticker).ratio()
        symbol_score = SequenceMatcher(None, query_lower, symbol).ratio()

        # Check for exact substring matches (higher weight)
        if query_lower in name:
            name_score = max(name_score, 0.9)
        if query_lower in ticker:
            ticker_score = max(ticker_score, 0.95)
        if query_lower in symbol:
            symbol_score = max(symbol_score, 0.95)

        # Use the highest score
        max_score = max(name_score, ticker_score, symbol_score)

        if max_score > 0.3:  # Threshold for relevance
            scored_assets.append((max_score, asset))

    # Sort by score descending
    scored_assets.sort(key=lambda x: x[0], reverse=True)

    # Return top results without scores
    return [asset for score, asset in scored_assets[:limit]]


@tool
def search_asset(symbol: str) -> str:
    """
    Search for stock/asset information by company name or ticker symbol.
    Performs fuzzy search and returns the most similar matches from Finam API.

    Args:
        symbol: Company name or ticker symbol to search for (e.g., "Gazprom", "SBER", "Apple")

    Returns:
        JSON string with list of matching assets including their symbols, tickers, names, and IDs
    """
    client = get_finam_client()

    # Get all available assets from the API
    response = client.execute_request("GET", "/v1/assets")

    if "error" in response:
        return f"Error fetching assets: {response.get('error')}"

    # The response should contain a list of assets
    assets = response.get("data", []) if isinstance(response, dict) else response

    if not isinstance(assets, list):
        return f"Unexpected API response format: {type(assets)}"

    # Perform fuzzy search
    matches = fuzzy_search_assets(symbol, assets, limit=5)

    if not matches:
        return f"No assets found matching '{symbol}'"

    # Format the results
    result = f"Found {len(matches)} matching asset(s) for '{symbol}':\n\n"
    for i, asset in enumerate(matches, 1):
        result += f"{i}. {asset.get('name', 'N/A')}\n"
        result += f"   Symbol: {asset.get('symbol', 'N/A')}\n"
        result += f"   Ticker: {asset.get('ticker', 'N/A')}\n"
        result += f"   ID: {asset.get('id', 'N/A')}\n"
        result += f"   Type: {asset.get('type', 'N/A')}\n"
        result += f"   MIC: {asset.get('mic', 'N/A')}\n"
        result += f"   ISIN: {asset.get('isin', 'N/A')}\n\n"

    return result


@tool
def get_quote(symbol: str) -> str:
    """
    Get current quote for a financial instrument.

    Args:
        symbol: Full symbol of the instrument (e.g., "SBER@MISX", "GAZP@TQBR")

    Returns:
        JSON string with current quote information including price, volume, etc.
    """
    client = get_finam_client()
    response = client.get_quote(symbol)

    if "error" in response:
        return f"Error fetching quote: {response.get('error')}"

    return str(response)


@tool
def get_orderbook(symbol: str, depth: int = 10) -> str:
    """
    Get order book (market depth) for a financial instrument.

    Args:
        symbol: Full symbol of the instrument (e.g., "SBER@MISX")
        depth: Number of levels to retrieve (default: 10)

    Returns:
        JSON string with order book including bids and asks
    """
    client = get_finam_client()
    response = client.get_orderbook(symbol, depth)

    if "error" in response:
        return f"Error fetching orderbook: {response.get('error')}"

    return str(response)


@tool
def get_candles(symbol: str, timeframe: str = "D") -> str:
    """
    Get historical candles (OHLCV data) for a financial instrument.

    Args:
        symbol: Full symbol of the instrument (e.g., "SBER@MISX")
        timeframe: Timeframe for candles (e.g., "D" for daily, "H" for hourly)

    Returns:
        JSON string with historical candles data
    """
    client = get_finam_client()
    response = client.get_candles(symbol, timeframe)

    if "error" in response:
        return f"Error fetching candles: {response.get('error')}"

    return str(response)


# List of all available tools
ALL_TOOLS = [
    search_asset,
    get_quote,
    get_orderbook,
    get_candles,
]
