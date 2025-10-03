# Agent System Usage Guide

## Quick Start

### 1. Installation

```bash
# Install dependencies
pip install langgraph langchain-core langchain-openai

# Or using the repository
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file:

```bash
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_MODEL=openai/gpt-4o-mini
OPENROUTER_BASE=https://openrouter.ai/api/v1
FINAM_API_BASE_URL=https://api.finam.ru
```

### 3. Basic Usage

#### Using the CLI

```bash
# Simple query
agent-cli "Найди информацию об акциях Газпром"

# With verbose output
agent-cli "Найди акции Apple" --verbose
```

#### Using Python

```python
from src.app.agents import run_agent_workflow

# Run a query
result = run_agent_workflow("Найди информацию об акциях Газпром")
print(result)
```

## Example Queries

### 1. Search for Russian Stocks

```python
result = run_agent_workflow("Найди акции Сбербанк")
```

**Expected Output:**
```
Found 2 matching asset(s) for 'Сбербанк':

1. Sberbank of Russia
   Symbol: SBER@MISX
   Ticker: SBER
   ID: 123456
   Type: EQUITIES
   MIC: MISX
   ISIN: RU0009029540

2. Sberbank - Preferred
   Symbol: SBERP@MISX
   Ticker: SBERP
   ID: 123457
   Type: EQUITIES
   MIC: MISX
   ISIN: RU0009029557
```

### 2. Search for American Stocks

```python
result = run_agent_workflow("Найди информацию об акциях Apple")
```

### 3. Search Multiple Assets

```python
result = run_agent_workflow("Найди акции Газпром, Лукойл и Роснефть")
```

## Advanced Usage

### Using Individual Tools

```python
from src.app.agents.tools import search_asset, get_quote, get_orderbook

# Search for an asset
result = search_asset.invoke({"symbol": "Газпром"})
print(result)

# Get quote (requires full symbol from search)
quote = get_quote.invoke({"symbol": "GAZP@TQBR"})
print(quote)

# Get orderbook
orderbook = get_orderbook.invoke({"symbol": "GAZP@TQBR", "depth": 5})
print(orderbook)
```

### Using the Graph Directly

```python
from src.app.agents import create_agent_graph
from langchain_core.messages import HumanMessage

# Create graph
graph = create_agent_graph()

# Define initial state
state = {
    "messages": [HumanMessage(content="Найди акции Яндекс")],
    "plan": "",
    "api_results": "",
    "final_answer": "",
    "next_agent": "route_agent",
}

# Execute
result = graph.invoke(state)
print(result["final_answer"])
```

### Custom Agent Logic

```python
from src.app.agents import create_api_agent, create_route_agent
from langchain_core.messages import HumanMessage, SystemMessage

# Create agents
api_agent = create_api_agent()
route_agent = create_route_agent()

# Use API agent directly
messages = [
    SystemMessage(content="You are an API agent for Finam"),
    HumanMessage(content="Search for Sberbank stocks")
]
response = api_agent.invoke(messages)
print(response)
```

## Workflow Visualization

```
┌─────────────────────────────────────────────────────────────┐
│                        User Query                            │
│              "Найди акции Газпром"                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    Route Agent                               │
│  • Analyzes query                                           │
│  • Determines it needs API data                             │
│  • Delegates to API Agent                                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                     API Agent                                │
│  • Uses search_asset tool                                   │
│  • Calls Finam API: GET /v1/assets                          │
│  • Performs fuzzy search on "Газпром"                       │
│  • Returns top 5 matches                                    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Route Agent (Synthesis)                         │
│  • Receives API results                                     │
│  • Formats for user                                         │
│  • Returns final answer in Russian                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   Final Answer                               │
│  Structured list of matching assets with details            │
└─────────────────────────────────────────────────────────────┘
```

## Tool Details

### search_asset

**Purpose:** Find financial instruments by name or ticker

**Algorithm:**
1. Fetches all assets from `/v1/assets`
2. Calculates similarity scores for name, ticker, symbol
3. Applies substring matching with higher weight
4. Filters by 0.3 similarity threshold
5. Returns top 5 matches

**Input:** Company name or ticker (partial match OK)

**Output:** List of matching assets with full details

### get_quote

**Purpose:** Get current market price and data

**Input:** Full symbol (e.g., "SBER@MISX")

**Output:** Current price, volume, bid/ask, etc.

### get_orderbook

**Purpose:** Get market depth (order book)

**Input:** 
- symbol: Full symbol
- depth: Number of levels (default: 10)

**Output:** Bids and asks with prices and volumes

### get_candles

**Purpose:** Get historical price data

**Input:**
- symbol: Full symbol
- timeframe: "D" (daily), "H" (hourly), etc.

**Output:** OHLCV data

## Error Handling

The system handles errors gracefully:

```python
# API not available
result = run_agent_workflow("Найди акции XYZ")
# Returns: "Error fetching assets: Connection refused"

# No matches found
result = run_agent_workflow("Найди акции NONEXISTENT")
# Returns: "No assets found matching 'NONEXISTENT'"

# Invalid symbol format
result = get_quote.invoke({"symbol": "INVALID"})
# Returns: "Error fetching quote: 404 Not Found"
```

## Performance Tips

1. **Cache results** when searching for the same assets multiple times
2. **Use specific queries** for better fuzzy search results
3. **Batch requests** when searching for multiple assets
4. **Set appropriate timeouts** for API calls

## Troubleshooting

### Issue: "OPENROUTER_API_KEY is not set"

**Solution:** Create a `.env` file with your API key

### Issue: "No module named 'langgraph'"

**Solution:** `pip install langgraph langchain-core langchain-openai`

### Issue: Agent returns empty results

**Solution:** Check your Finam API access and network connectivity

### Issue: Fuzzy search not finding assets

**Solution:** Try different query variations (company name vs ticker)

## Next Steps

- Read the full documentation in `docs/agents.md`
- Run the demo: `python examples/demo_agents.py`
- Explore the tests: `pytest tests/test_agents.py -v`
- Try the CLI: `agent-cli "your query here"`
