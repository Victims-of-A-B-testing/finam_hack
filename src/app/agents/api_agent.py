"""
API Agent for working with Finam API
"""

from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI

from ..core.config import get_settings
from .state import AgentState
from .tools import ALL_TOOLS


def create_api_agent() -> ChatOpenAI:
    """Create the API agent with tools."""
    settings = get_settings()

    # Create LLM with tools
    llm = ChatOpenAI(
        model=settings.openrouter_model,
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base,
        temperature=0.2,
    )

    # Bind tools to the LLM
    return llm.bind_tools(ALL_TOOLS)


def api_agent_node(state: AgentState) -> dict:
    """
    API Agent node that processes user requests and uses tools to interact with Finam API.

    This agent:
    1. Receives a task from the route agent
    2. Uses available tools (search_asset, get_quote, etc.) to fetch data
    3. Returns results to be used by other agents or returned to user
    """
    api_agent = create_api_agent()

    # Get the last message (should be the task from route agent)
    messages = state["messages"]

    # Add system prompt
    system_prompt = SystemMessage(content="""You are an API agent specialized in working with Finam TradeAPI.
Your job is to:
1. Use the search_asset tool to find assets when given a company name or ticker
2. Return the most relevant results from the search
3. If asked for more details (quote, orderbook, candles), use the appropriate tools with the correct symbol format

When searching for assets, always use the search_asset tool with the company name or ticker.
The tool will return matches with their full symbols (e.g., "SBER@MISX").

Be concise and return structured information.""")

    # Invoke the agent with system prompt + messages
    response = api_agent.invoke([system_prompt, *messages])

    # Store API results
    api_results = response.content if hasattr(response, "content") else str(response)

    return {
        "messages": [response],
        "api_results": api_results,
        "next_agent": "route_agent"  # Return control to route agent
    }
