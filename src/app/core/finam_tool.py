"""
Finam API Tool for smolagents
"""

from typing import Any, ClassVar

from smolagents import Tool

from ..adapters.finam_client import FinamAPIClient


class FinamAPITool(Tool):
    """
    Tool that allows executing requests to Finam TradeAPI.

    This tool wraps the FinamAPIClient.execute_request method to make it available
    to the smolagents agent for making API calls.
    """

    name = "finam_api_execute"
    description = """
    Executes HTTP requests to Finam TradeAPI.

    Args:
        method: HTTP method (GET, POST, DELETE, etc.)
        path: API path (e.g., /v1/instruments/SBER@MISX/quotes/latest)
        params: Optional query parameters as a dict (e.g., {"depth": 10})
        json_data: Optional JSON body for POST requests as a dict

    Returns:
        dict: API response as a dictionary, or error details if request failed

    Examples:
        - Get quote: execute_request("GET", "/v1/instruments/SBER@MISX/quotes/latest")
        - Get orderbook: execute_request("GET", "/v1/instruments/SBER@MISX/orderbook", params={"depth": 10})
        - Get account: execute_request("GET", "/v1/accounts/ACC-001-A")
    """

    inputs: ClassVar[dict[str, dict[str, Any]]] = {
        "method": {
            "type": "string",
            "description": "HTTP method (GET, POST, DELETE, etc.)",
        },
        "path": {
            "type": "string",
            "description": "API path starting with /v1/",
        },
        "params": {
            "type": "string",
            "description": "Optional JSON string of query parameters",
            "nullable": True,
        },
        "json_data": {
            "type": "string",
            "description": "Optional JSON string of request body",
            "nullable": True,
        },
    }
    output_type = "string"

    def __init__(self, client: FinamAPIClient | None = None, **kwargs: Any) -> None:  # noqa: ANN401
        """Initialize the tool with a FinamAPIClient"""
        super().__init__(**kwargs)
        self.client = client or FinamAPIClient()

    def forward(
        self, method: str, path: str, params: str | None = None, json_data: str | None = None
    ) -> dict[str, Any]:
        """
        Execute an HTTP request to Finam TradeAPI

        Args:
            method: HTTP method (GET, POST, DELETE, etc.)
            path: API path (e.g., /v1/instruments/SBER@MISX/quotes/latest)
            params: Optional JSON string of query parameters
            json_data: Optional JSON string of request body

        Returns:
            dict: API response or error details
        """
        import json

        kwargs: dict[str, Any] = {}

        # Parse params if provided
        if params:
            try:
                if isinstance(params, str):
                    kwargs["params"] = json.loads(params)
                else:
                    kwargs["params"] = params
            except json.JSONDecodeError as e:
                return {"error": f"Invalid params JSON: {e}"}

        # Parse json_data if provided
        if json_data:
            try:
                if isinstance(json_data, str):
                    kwargs["json"] = json.loads(json_data)
                else:
                    kwargs["json"] = json_data
            except json.JSONDecodeError as e:
                return {"error": f"Invalid json_data JSON: {e}"}

        # Execute the request
        return self.client.execute_request(method, path, **kwargs)
