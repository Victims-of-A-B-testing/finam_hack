"""
Tests for LangGraph agent system
"""

import pytest
from unittest.mock import MagicMock, patch

from src.app.agents import search_asset, get_quote
from src.app.agents.tools import fuzzy_search_assets


class TestFuzzySearch:
    """Test fuzzy search functionality."""

    def test_fuzzy_search_by_ticker(self):
        """Test fuzzy search by ticker."""
        assets = [
            {"symbol": "SBER@MISX", "ticker": "SBER", "name": "Sberbank"},
            {"symbol": "GAZP@TQBR", "ticker": "GAZP", "name": "Gazprom"},
        ]

        results = fuzzy_search_assets("SBER", assets, limit=5)
        assert len(results) >= 1
        assert results[0]["ticker"] == "SBER"

    def test_fuzzy_search_by_name(self):
        """Test fuzzy search by company name."""
        assets = [
            {"symbol": "SBER@MISX", "ticker": "SBER", "name": "Sberbank"},
            {"symbol": "GAZP@TQBR", "ticker": "GAZP", "name": "Gazprom"},
        ]

        results = fuzzy_search_assets("Gazprom", assets, limit=5)
        assert len(results) >= 1
        assert "Gazprom" in results[0]["name"]

    def test_fuzzy_search_partial_match(self):
        """Test fuzzy search with partial match."""
        assets = [
            {"symbol": "SBER@MISX", "ticker": "SBER", "name": "Sberbank of Russia"},
            {"symbol": "GAZP@TQBR", "ticker": "GAZP", "name": "Gazprom PJSC"},
        ]

        results = fuzzy_search_assets("Sber", assets, limit=5)
        assert len(results) >= 1

    def test_fuzzy_search_limit(self):
        """Test that fuzzy search respects limit."""
        assets = [
            {"symbol": f"TEST{i}@MISX", "ticker": f"TEST{i}", "name": f"Test Company {i}"}
            for i in range(10)
        ]

        results = fuzzy_search_assets("Test", assets, limit=3)
        assert len(results) <= 3


class TestTools:
    """Test agent tools."""

    @patch("src.app.agents.tools.get_finam_client")
    def test_search_asset_tool(self, mock_get_client):
        """Test search_asset tool."""
        mock_client = MagicMock()
        mock_client.execute_request.return_value = {
            "data": [
                {
                    "symbol": "SBER@MISX",
                    "id": "123",
                    "ticker": "SBER",
                    "name": "Sberbank",
                    "type": "EQUITIES",
                    "mic": "MISX",
                    "isin": "RU0009029540",
                }
            ]
        }
        mock_get_client.return_value = mock_client

        result = search_asset.invoke({"symbol": "SBER"})
        assert "SBER" in result
        assert "Sberbank" in result

    @patch("src.app.agents.tools.get_finam_client")
    def test_get_quote_tool(self, mock_get_client):
        """Test get_quote tool."""
        mock_client = MagicMock()
        mock_client.get_quote.return_value = {"price": 100.0, "volume": 1000}
        mock_get_client.return_value = mock_client

        result = get_quote.invoke({"symbol": "SBER@MISX"})
        assert "100.0" in result
