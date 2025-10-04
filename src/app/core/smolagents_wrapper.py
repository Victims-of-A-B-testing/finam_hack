import smolagents
from smolagents import CodeAgent, OpenAIModel, WebSearchTool, tool, Tool
from typing import Any, Dict, List
# from config import get_settings
from app.adapters.finam_client import FinamAPIClient
# from Levenshtein import distance
# from transliterate import translit
from textwrap import dedent

# _s = get_settings()
# _finam_client = FinamAPIClient(_s.finam_api_key, _s.finam_api_base)

# @tool
# def find_asset_name(string: str) -> str:
#     """
#     Finds the closest matching asset symbol names to a given input string.

#     Args:
#         string (str): The input string to match against available asset names.

#     Returns:
#         List[str]: A list of up to 10 asset names most similar to the input string, sorted by similarity.

#     Note:
#         This function queries the Finam API for all available assets and uses a string distance metric
#         to determine the closest matches.

#     Example:
#         >>> find_asset_name("appl")
#         ['AAPL', 'APPLX', ...]
#     """
#     all_assets = _finam_client.execute_request("GET", "/v1/assets")
#     # print(all_assets)
#     # Try transliteration if input is Russian or English

#     candidates = []
#     # Original input
#     # candidates.append(string)
#     # Transliterate Russian to English
#     try:
#         candidates.append(translit(string, 'ru', reversed=True))
#     except Exception:
#         pass
#     # Transliterate English to Russian
#     try:
#         candidates.append(translit(string, 'ru'))
#     except Exception:
#         pass

#     # Remove duplicates and empty
#     candidates = list({c for c in candidates if c and isinstance(c, str)})

#     # print(candidates)

#     # Find closest for each candidate
#     closest_names = []
#     for cand in candidates:
#         closest = sorted(
#             all_assets.get("assets", []),
#             key=lambda a: distance(a["name"].lower(), cand.lower())
#         )[:3]
#         closest_names.extend(closest)

#     # Remove duplicates by asset name
#     seen = set()
#     unique_closest = []
#     for a in closest_names:
#         if a["name"] not in seen:
#             unique_closest.append(a)
#             seen.add(a["name"])

#     return unique_closest


# Corrected Toolkit Implementation
class FinamAPIToolkit:
    """
    A toolkit for creating smol-agent tools from the FinamAPIClient.
    """

    def __init__(self, client: FinamAPIClient):
        self.client = client

    def get_tools(self) -> List[Tool]:
        """
        Returns a list of smol-agent tools for each method of the FinamAPIClient.
        """
        tools = [
            self._create_tool_for_method(
                method_name="find_asset_name",
                description="Find the closest matching asset names.",
                inputs={"string": {"type": "string", "description": "Company name or ticker symbol."}},
            ),
            self._create_tool_for_method(
                method_name="get_quote",
                description="Get the current quote for a financial instrument.",
                inputs={"symbol": {"type": "string", "description": "The instrument symbol."}},
            ),
            self._create_tool_for_method(
                method_name="get_orderbook",
                description="Get the order book for a financial instrument.",
                inputs={
                    "symbol": {"type": "string", "description": "The instrument symbol."},
                    "depth": {"type": "integer", "description": "The depth of the order book.", "default": 10},
                },
            ),
            self._create_tool_for_method(
                method_name="get_candles",
                description="Get historical candle data for a financial instrument.",
                inputs={
                    "symbol": {"type": "string", "description": "The instrument symbol."},
                    "timeframe": {"type": "string", "description": "The timeframe of the candles (e.g., 'D' for daily).", "default": "D"},
                    "start": {"type": "string", "description": "The start time for the data in ISO format.", "required": False},
                    "end": {"type": "string", "description": "The end time for the data in ISO format.", "required": False},
                },
            ),
            self._create_tool_for_method(
                method_name="get_account",
                description="Get information about a trading account.",
                inputs={"account_id": {"type": "string", "description": "The account ID."}},
            ),
            self._create_tool_for_method(
                method_name="get_orders",
                description="Get a list of orders for a trading account.",
                inputs={"account_id": {"type": "string", "description": "The account ID."}},
            ),
            self._create_tool_for_method(
                method_name="get_order",
                description="Get information about a specific order.",
                inputs={
                    "account_id": {"type": "string", "description": "The account ID."},
                    "order_id": {"type": "string", "description": "The order ID."},
                },
            ),
            self._create_tool_for_method(
                method_name="create_order",
                description="Create a new order.",
                inputs={
                    "account_id": {"type": "string", "description": "The account ID."},
                    "order_data": {"type": "object", "description": "The order data as a dictionary."},
                },
            ),
            self._create_tool_for_method(
                method_name="cancel_order",
                description="Cancel an existing order.",
                inputs={
                    "account_id": {"type": "string", "description": "The account ID."},
                    "order_id": {"type": "string", "description": "The order ID to cancel."},
                },
            ),
            self._create_tool_for_method(
                method_name="get_trades",
                description="Get the trade history for a trading account.",
                inputs={
                    "account_id": {"type": "string", "description": "The account ID."},
                    "start": {"type": "string", "description": "The start time for the data in ISO format.", "required": False},
                    "end": {"type": "string", "description": "The end time for the data in ISO format.", "required": False},
                },
            ),
            self._create_tool_for_method(
                method_name="get_positions",
                description="Get the open positions for a trading account.",
                inputs={"account_id": {"type": "string", "description": "The account ID."}},
            ),
            self._create_tool_for_method(
                method_name="get_session_details",
                description="Get details about the current API session.",
                inputs={},
            ),
        ]
        return tools

    def _create_tool_for_method(
        self, method_name: str, description: str, inputs: Dict[str, Any]
    ) -> Tool:
        """
        A factory method to dynamically create a smol-agent Tool class with the
        correct `forward` method signature for a given FinamAPIClient method.
        """
        client_method = getattr(self.client, method_name)
        arg_names = list(inputs.keys())
        
        # Define the forward method with the correct signature dynamically
        def create_forward_method(method):
            # Create the source code for the forward method
            # Example: "def forward(self, symbol):\n    return method(symbol=symbol)"
            args_for_signature = ", ".join(['self'] + arg_names)
            args_for_call = ", ".join(f"{name}={name}" for name in arg_names)
            
            # Using dedent to keep formatting clean
            forward_method_code = dedent(f"""
                def forward({args_for_signature}):
                    return method({args_for_call})
            """)

            # Execute the code in a specific namespace to "compile" the function
            local_scope = {}
            exec(forward_method_code, {'method': method}, local_scope)
            return local_scope['forward']

        # Create the custom Tool class using the type factory
        tool_class_name = f"Finam{method_name.replace('_', ' ').title().replace(' ', '')}Tool"
        
        ToolClass = type(
            tool_class_name,
            (Tool,),
            {
                "name": f"finam_{method_name}",
                "description": description,
                "inputs": inputs,
                "output_type": "object",
                "forward": create_forward_method(client_method),
                # The __init__ is necessary to call the parent's __init__
                "__init__": lambda self: Tool.__init__(self),
            }
        )

        return ToolClass()
# print(find_asset_name("Сбербанк"))
# exit()

# print("Using model:", _s.openrouter_model)
# _model = OpenAIModel(
#     model_id=_s.openrouter_model, 
#     api_base=_s.openrouter_base,
#     api_key=_s.openrouter_api_key)

# _plot_agent = CodeAgent(
#     instructions="You are an expert in data visualization. Create plots using plotly based on user requests. Return plots as plotly JSON.",
#     tools=[], model=_model, additional_authorized_imports=["plotly"],
#     name="plot_agent",
#     description="Can create and show plots using plotly. Return plotly json"
# )

# toolkit = FinamAPIToolkit(_finam_client)

# # 3. Get the list of tools
# finam_tools = toolkit.get_tools()
# _finam_agent = CodeAgent(
#     instructions="""You are an expert in Finam TradeAPI. Answer questions about stocks, ETFs, bonds, currencies, and other assets traded using only the Finam TradeAPI. Use the provided tool to find correct asset symbol names when needed. Output API requests in the format: API_REQUEST: METHOD /path. Use GET, POST, DELETE methods as needed. If the request is not related to Finam TradeAPI, respond that you can only answer questions related to Finam TradeAPI.""",
#     tools=[find_asset_name] + finam_tools, model=_model,
#     name="finam_agent",
#     description="Can query Finam TradeAPI. Use find_asset_name to get correct asset symbol names",
#     additional_authorized_imports=["requests"]
# )

# _manager_agent = CodeAgent(
#     instructions="""You are a manager agent that can manage other agents. You have access to the following agents: finam_agent, plot_agent. Based on user requests, decide which agent to delegate the task to. If the request involves data visualization, use the plot_agent. For all other Finam TradeAPI related queries, use the finam_agent. If unsure, default to finam_agent.
#     Ты - AI ассистент трейдера, работающий с Finam TradeAPI.

# Твоя задача - помогать пользователю анализировать рынки и управлять портфелем.

# Когда пользователь задает вопрос, ты должен:
# 1. Определить, какой API запрос нужен
# 2. Сформулировать запрос в формате: HTTP_METHOD /api/path
# 3. Я выполню этот запрос и верну результат
# 4. Ты должен проанализировать результат и дать понятный ответ пользователю

# Доступные API endpoints:
# - GET /v1/instruments/{symbol}/quotes/latest - текущая котировка
# - GET /v1/instruments/{symbol}/orderbook - биржевой стакан
# - GET /v1/instruments/{symbol}/bars - исторические свечи
# - GET /v1/accounts/{account_id} - информация о счете и позициях
# - GET /v1/accounts/{account_id}/orders - список ордеров
# - POST /v1/accounts/{account_id}/orders - создание ордера
# - DELETE /v1/accounts/{account_id}/orders/{order_id} - отмена ордера

# Формат твоего ответа должен быть таким:
# ```
# API_REQUEST: GET /v1/instruments/SBER@MISX/quotes/latest

# <После получения ответа от API, проанализируй его и дай понятное объяснение>
# ```

# Отвечай на русском языке, будь полезным и дружелюбным.""",
#     tools=[], model=_model, managed_agents=[_finam_agent, _plot_agent],
#     name="manager_agent",
#     description="Can manage other agents"
# )


# # a = _manager_agent.run("Что в стакане по Газпрому?", return_full_result=True)
# # print(a)

def create_smolagent(s):
    _model = OpenAIModel(
        model_id=s.openrouter_model, 
        api_base=s.openrouter_base,
        api_key=s.openrouter_api_key)

    _plot_agent = CodeAgent(
        instructions="You are an expert in data visualization. Create plots using plotly based on user requests. Return plots as plotly JSON.",
        tools=[], model=_model, additional_authorized_imports=["plotly"],
        name="plot_agent",
        description="Can create and show plots using plotly. Return plotly json",
        return_full_result=True
    )

    toolkit = FinamAPIToolkit(FinamAPIClient(s.finam_api_key, s.finam_api_base))

    # 3. Get the list of tools
    finam_tools = toolkit.get_tools()
    _finam_agent = CodeAgent(
        instructions="""You are an expert in Finam TradeAPI. Answer questions about stocks, ETFs, bonds, currencies, and other assets traded using only the Finam TradeAPI. Use the provided tool to find correct asset symbol names when needed. Output API requests in the format: API_REQUEST: METHOD /path. Use GET, POST, DELETE methods as needed. If the request is not related to Finam TradeAPI, respond that you can only answer questions related to Finam TradeAPI.""",
        tools=finam_tools, model=_model,
        name="finam_agent",
        description="Can query Finam TradeAPI. Use find_asset_name to get correct asset symbol names",
        additional_authorized_imports=["requests"],
        return_full_result=True
    )

    _manager_agent = CodeAgent(
        instructions="""You are a manager agent that can manage other agents. You have access to the following agents: finam_agent, plot_agent. Based on user requests, decide which agent to delegate the task to. If the request involves data visualization, use the plot_agent. For all other Finam TradeAPI related queries, use the finam_agent. If unsure, default to finam_agent.
        Ты - AI ассистент трейдера, работающий с Finam TradeAPI.

    Твоя задача - помогать пользователю анализировать рынки и управлять портфелем.

    Когда пользователь задает вопрос, ты должен:
    1. Определить, какой API запрос нужен
    2. Сформулировать запрос в формате: HTTP_METHOD /api/path
    3. Я выполню этот запрос и верну результат
    4. Ты должен проанализировать результат и дать понятный ответ пользователю

    Доступные API endpoints:
    - GET /v1/instruments/{symbol}/quotes/latest - текущая котировка
    - GET /v1/instruments/{symbol}/orderbook - биржевой стакан
    - GET /v1/instruments/{symbol}/bars - исторические свечи
    - GET /v1/accounts/{account_id} - информация о счете и позициях
    - GET /v1/accounts/{account_id}/orders - список ордеров
    - POST /v1/accounts/{account_id}/orders - создание ордера
    - DELETE /v1/accounts/{account_id}/orders/{order_id} - отмена ордера

    Формат твоего ответа должен быть таким:
    ```
    API_REQUEST: GET /v1/instruments/SBER@MISX/quotes/latest

    <После получения ответа от API, проанализируй его и дай понятное объяснение>
    ```

    Если plot_agent вернул json с графиком, вставь его в ответ в формате:
    ```
    PLOTLY_JSON: {json}
    ```
    Отвечай на русском языке, будь полезным и дружелюбным.
    """,
        tools=[], model=_model, managed_agents=[_finam_agent, _plot_agent],
        name="manager_agent",
        description="Can manage other agents",
        return_full_result=True
    )
    return _manager_agent

# agent = create_smolagent(FinamAPIClient(_s.finam_api_key, _s.finam_api_base))
# print(agent.run("Что в стакане по Газпрому?"))