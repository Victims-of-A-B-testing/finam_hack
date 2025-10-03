# LangGraph Agent System

## Overview

This is a LangGraph-based agent system for interacting with the Finam TradeAPI. The system consists of two main agents:

1. **Route Agent** - Coordinates tasks and delegates to specialized agents
2. **API Agent** - Interacts with Finam API to search for assets and retrieve market data

## Architecture

```
User Query
    ↓
Route Agent (Planner & Coordinator)
    ↓
API Agent (Specialized for Finam API)
    ↓
Route Agent (Synthesizer)
    ↓
Final Answer
```

## Agents

### 1. Route Agent

The Route Agent is responsible for:
- Analyzing user requests
- Creating execution plans
- Delegating tasks to specialized agents (API Agent)
- Synthesizing results from agents into final answers

**Key Features:**
- Plans multi-step workflows
- Delegates to appropriate agents based on request type
- Aggregates and formats results for user

### 2. API Agent

The API Agent specializes in:
- Searching for financial instruments by name or ticker
- Retrieving quotes, orderbooks, and candles
- Working with Finam TradeAPI endpoints

**Key Features:**
- Fuzzy search for asset matching
- Multiple tool support (search_asset, get_quote, get_orderbook, get_candles)
- Handles API errors gracefully

## Tools

The agent system includes the following tools:

### search_asset(symbol: str)
Performs fuzzy search on assets from Finam API. Searches by:
- Company name (e.g., "Gazprom", "Сбербанк")
- Ticker symbol (e.g., "SBER", "GAZP")
- Partial matches

Returns top 5 most relevant matches with full details.

**Example:**
```python
from src.app.agents import search_asset

result = search_asset.invoke({"symbol": "Газпром"})
# Returns: List of matching assets with symbol, ticker, name, ID, etc.
```

### get_quote(symbol: str)
Gets current quote for a financial instrument.

**Example:**
```python
from src.app.agents import get_quote

result = get_quote.invoke({"symbol": "SBER@MISX"})
# Returns: Current price, volume, etc.
```

### get_orderbook(symbol: str, depth: int)
Gets market depth (order book) for an instrument.

**Example:**
```python
from src.app.agents import get_orderbook

result = get_orderbook.invoke({"symbol": "SBER@MISX", "depth": 10})
# Returns: Bids and asks with prices and volumes
```

### get_candles(symbol: str, timeframe: str)
Gets historical OHLCV data.

**Example:**
```python
from src.app.agents import get_candles

result = get_candles.invoke({"symbol": "SBER@MISX", "timeframe": "D"})
# Returns: Historical candles data
```

## Usage

### Basic Usage

```python
from src.app.agents import run_agent_workflow

# Simple query
result = run_agent_workflow("Найди информацию об акциях Газпром")
print(result)
```

### Advanced Usage

```python
from src.app.agents import create_agent_graph
from langchain_core.messages import HumanMessage

# Create the agent graph
graph = create_agent_graph()

# Initial state
initial_state = {
    "messages": [HumanMessage(content="Найди акции Сбербанк")],
    "plan": "",
    "api_results": "",
    "final_answer": "",
    "next_agent": "route_agent",
}

# Run the graph
result = graph.invoke(initial_state)
print(result["final_answer"])
```

## Running the Demo

```bash
# Set up environment
cp .env.example .env
# Edit .env and add your OPENROUTER_API_KEY

# Run the demo
python examples/demo_agents.py
```

## Testing

Run the tests:

```bash
pytest tests/test_agents.py -v
```

## Configuration

Set the following environment variables in your `.env` file:

```bash
# Required
OPENROUTER_API_KEY=your_api_key_here

# Optional
OPENROUTER_MODEL=openai/gpt-4o-mini
OPENROUTER_BASE=https://openrouter.ai/api/v1
FINAM_ACCESS_TOKEN=your_finam_token
FINAM_API_BASE_URL=https://api.finam.ru
```

## Fuzzy Search Algorithm

The fuzzy search uses Python's `difflib.SequenceMatcher` to find similar assets:

1. Calculates similarity ratios for name, ticker, and symbol
2. Gives extra weight to exact substring matches
3. Returns top N results sorted by similarity score
4. Filters out results below 0.3 similarity threshold

## Error Handling

The agents handle errors gracefully:
- API errors are caught and formatted for user
- Invalid symbols return helpful error messages
- Network issues are logged and reported

## Future Enhancements

Potential improvements:
- Add more specialized agents (Portfolio Analyst, Market Scanner, Backtester)
- Implement caching for frequently accessed data
- Add streaming responses for long-running tasks
- Support for multiple languages beyond Russian
- Integration with more data sources

## Dependencies

- `langgraph` - Agent orchestration framework
- `langchain-core` - Core LangChain abstractions
- `langchain-openai` - OpenAI/OpenRouter integration
- `requests` - HTTP client for API calls

## License

MIT License - See parent project for details
