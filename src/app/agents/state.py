"""
State management for LangGraph agent workflow
"""

from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """State for the agent workflow."""

    # Messages exchanged between user and agents
    messages: Annotated[list, add_messages]

    # Current plan from route agent
    plan: str

    # Results from API agent
    api_results: str

    # Final answer to return to user
    final_answer: str

    # Next agent to invoke
    next_agent: str
