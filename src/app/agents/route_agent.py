"""
Route Agent for planning and task delegation
"""

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from ..core.config import get_settings
from .state import AgentState


def create_route_agent() -> ChatOpenAI:
    """Create the route agent."""
    settings = get_settings()

    return ChatOpenAI(
        model=settings.openrouter_model,
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base,
        temperature=0.3,
    )


def route_agent_node(state: AgentState) -> dict:
    """
    Route Agent node that builds plans and delegates tasks to other agents.

    This agent:
    1. Analyzes user requests
    2. Creates a plan for how to handle the request
    3. Delegates to appropriate specialized agents (API agent, etc.)
    4. Synthesizes final answers from agent results
    """
    route_agent = create_route_agent()

    messages = state["messages"]
    api_results = state.get("api_results", "")

    # System prompt for the route agent
    system_prompt = SystemMessage(
        content="""You are a route agent that coordinates tasks and delegates to specialized agents.

Available agents:
1. api_agent - Searches for assets, gets quotes, orderbooks, and candles from Finam API

Your responsibilities:
1. Analyze user requests
2. Create a plan for handling the request
3. Delegate to the api_agent when market data is needed
4. Synthesize results into clear, helpful answers

When a user asks about a stock or company:
- First, delegate to api_agent to search for the asset
- The api_agent will use tools to find matching assets
- Once you have results, present them clearly to the user

Respond in Russian. Be helpful and concise."""
    )

    # Check if we have API results to synthesize
    if api_results:
        # We have results from API agent, synthesize final answer
        synthesis_prompt = HumanMessage(
            content=f"""Based on the following API results, provide a clear and helpful answer to the user:

API Results:
{api_results}

Synthesize this information and present it in a user-friendly way in Russian.""")

        response = route_agent.invoke([system_prompt, *messages, synthesis_prompt])

        return {
            "messages": [response],
            "final_answer": response.content if hasattr(response, "content") else str(response),
            "next_agent": "END"  # We're done
        }
    # No API results yet, analyze request and delegate
    planning_prompt = HumanMessage(
        content="""Analyze the user's request and determine if you need to delegate to the api_agent.

If the user is asking about a company, stock, or market data, respond with:
DELEGATE: api_agent - [brief description of what the api_agent should do]

If you can answer directly without market data, provide the answer directly."""
    )

    response = route_agent.invoke([system_prompt, *messages, planning_prompt])
    response_text = response.content if hasattr(response, "content") else str(response)

    # Check if we need to delegate
    if "DELEGATE: api_agent" in response_text:
        # Extract the task for the API agent
        task = (
            response_text.split("DELEGATE: api_agent -")[1].strip()
            if "-" in response_text
            else messages[-1].content
        )

        return {
            "messages": [HumanMessage(content=task)],
            "plan": response_text,
            "next_agent": "api_agent"
        }
    # Can answer directly
    return {
    "messages": [response],
    "final_answer": response_text,
    "next_agent": "END"
    }


def should_continue(state: AgentState) -> str:
    """
    Determine which agent to invoke next based on the state.

    Returns:
        Name of the next agent to invoke or "END" to finish
    """
    return state.get("next_agent", "END")
