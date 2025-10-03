"""
LangGraph workflow for agent system
"""

from langchain_core.messages import HumanMessage
from langgraph.graph import END, StateGraph

from .api_agent import api_agent_node
from .route_agent import route_agent_node, should_continue
from .state import AgentState


def create_agent_graph() -> StateGraph:
    """
    Create the agent workflow graph.

    Flow:
    1. User input -> Route Agent
    2. Route Agent analyzes and either:
       a. Delegates to API Agent -> API Agent -> Route Agent (for synthesis) -> END
       b. Answers directly -> END
    """
    # Create the graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("route_agent", route_agent_node)
    workflow.add_node("api_agent", api_agent_node)

    # Set entry point
    workflow.set_entry_point("route_agent")

    # Add conditional edges from route_agent
    workflow.add_conditional_edges(
        "route_agent",
        should_continue,
        {
            "api_agent": "api_agent",
            "END": END,
        }
    )

    # API agent always returns to route agent for synthesis
    workflow.add_edge("api_agent", "route_agent")

    # Compile the graph
    return workflow.compile()


def run_agent_workflow(user_input: str) -> str:
    """
    Run the agent workflow with user input.

    Args:
        user_input: User's question or request

    Returns:
        Final answer from the agent system
    """
    graph = create_agent_graph()

    # Initial state
    initial_state = {
        "messages": [HumanMessage(content=user_input)],
        "plan": "",
        "api_results": "",
        "final_answer": "",
        "next_agent": "route_agent",
    }

    # Run the graph
    result = graph.invoke(initial_state)

    # Return the final answer
    return result.get("final_answer", "No answer generated")
