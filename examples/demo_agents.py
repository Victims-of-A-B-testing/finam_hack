#!/usr/bin/env python3
"""
Demo script for LangGraph agent system

This script demonstrates how to use the agent system to interact with Finam API.

Usage:
    python examples/demo_agents.py
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.app.agents import run_agent_workflow


def demo_basic_search() -> None:
    """Demo: Search for assets."""
    print("\n" + "=" * 80)
    print("DEMO 1: Поиск активов")
    print("=" * 80)

    query = "Найди информацию об акциях Газпром"
    print(f"\n📝 User Query: {query}\n")

    try:
        result = run_agent_workflow(query)
        print(f"🤖 Agent Response:\n{result}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


def demo_multiple_assets() -> None:
    """Demo: Search for multiple assets."""
    print("\n" + "=" * 80)
    print("DEMO 2: Поиск нескольких активов")
    print("=" * 80)

    query = "Найди акции Сбербанк, Газпром и Яндекс"
    print(f"\n📝 User Query: {query}\n")

    try:
        result = run_agent_workflow(query)
        print(f"🤖 Agent Response:\n{result}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


def demo_american_stock() -> None:
    """Demo: Search for American stock."""
    print("\n" + "=" * 80)
    print("DEMO 3: Поиск американских акций")
    print("=" * 80)

    query = "Найди информацию об акциях Apple"
    print(f"\n📝 User Query: {query}\n")

    try:
        result = run_agent_workflow(query)
        print(f"🤖 Agent Response:\n{result}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


def main() -> int:
    """Run all demos."""
    print("\n🚀 LangGraph Agent System Demo")
    print("=" * 80)

    # Check if API keys are configured
    from src.app.core.config import get_settings

    try:
        settings = get_settings()
        print(f"✓ OpenRouter API Key: {'configured' if settings.openrouter_api_key else 'NOT SET'}")
        print(f"✓ OpenRouter Model: {settings.openrouter_model}")
        print(f"✓ OpenRouter Base URL: {settings.openrouter_base}")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        print("\nPlease set up your .env file with OPENROUTER_API_KEY")
        return 1

    # Run demos
    try:
        demo_basic_search()
        # Uncomment to run more demos
        # demo_multiple_assets()
        # demo_american_stock()

        print("\n" + "=" * 80)
        print("✓ Demo completed successfully!")
        print("=" * 80 + "\n")
        return 0
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
