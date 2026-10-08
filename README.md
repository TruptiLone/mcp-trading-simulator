# MCP Trading Simulator

A paper-trading application that connects AI agents to account tools, market quotes, web research and persistent memory through the Model Context Protocol. A FastAPI service and TypeScript dashboard show four simulated portfolios, transactions and agent activity.

**A runnable no-key demo is included.** It uses deterministic fixture orders and prices, not AI decisions. The application does not connect to a brokerage or place real orders.

## What it demonstrates

- Custom MCP tools for balances, holdings, simulated orders and strategy updates.
- MCP resources for account snapshots and strategies, exposed over stdio.
- A researcher agent exposed as a tool, with fetch, optional Tavily search and per-persona memory.
- Four strategy personas coordinated in bounded parallel agent rounds.
- SQLite persistence and activity logs, consumed by a FastAPI/TypeScript dashboard.
- Input validation, explicit quote-source modes, tested P&L accounting and five solution notebooks.

## Quick start: no API keys

Requires Python 3.12+ and uv. The MCP dependency is constrained to v1 because this project uses `mcp.server.fastmcp`.

```bash
uv sync
uv run python -m examples.offline_demo
uv run python -m examples.mcp_roundtrip
MARKET_MODE=fixture uv run uvicorn backend.api:app --host 127.0.0.1 --port 8000
```

The demo creates four paper accounts under ignored `artifacts/`. A second run refuses to overwrite existing demo accounts unless `--reset` is supplied. The MCP roundtrip uses temporary storage and starts a real local MCP server.

For the dashboard, use Node.js 20+ and npm in a second terminal:

```bash
cd frontend
npm ci
npm run dev
```

Open **http://localhost:5174**. Keep `MARKET_MODE=fixture` on the API when reviewing fixture data. The frontend uses a local API proxy on port 8000. A compiled frontend alone needs an equivalent `/api` reverse proxy when deployed.

## Optional agent run

```bash
uv sync --extra agents
cp .env.example .env
# Set OPENAI_API_KEY and a TRADER_MODEL available in your account.
# Optionally set TAVILY_API_KEY for search.
uv run python -m backend.reset --confirm
uv run python -m backend.trading_floor --rounds 1
```

The reset command replaces the four simulation accounts. Agent runs use external model APIs and can incur charges. Node/npx and uvx are needed for research MCP servers. External notifications are disabled by default; summaries go to the local log. Provider-specific credentials are required only when selecting that provider.

`MARKET_MODE=simulated` uses synthetic time-varying quotes. `fixture` uses fixed test quotes. `live` requires `uv sync --extra live-market` and a Massive key and uses previous closing prices, not real-time execution prices. All modes retain paper-only accounts. Live quote failures do not silently switch to synthetic data.

## Solution notebooks and Python examples

| Notebook | Coverage | Python entry point |
| --- | --- | --- |
| [01 MCP tools and resources](notebooks/01_mcp_tools_and_resources.ipynb) | Real stdio discovery, calls, resources; optional remote HTTP | `python -m examples.mcp_roundtrip` |
| [02 Simulated accounts](notebooks/02_simulated_account_server.ipynb) | Orders, validation, persistence, cash-flow accounting | `backend/accounts.py`, `backend/accounts_server.py` |
| [03 Context and research](notebooks/03_context_and_research.ipynb) | Fetch, filesystem, memory, search; optional Qdrant discovery | `python -m examples.research_agent "your question"` |
| [04 Multi-agent simulation](notebooks/04_multi_agent_simulation.ipynb) | Fixture demo and optional bounded agent round | `python -m examples.offline_demo`, `python -m backend.trading_floor` |
| [05 API and observability](notebooks/05_api_and_observability.ipynb) | Portfolio API, logs and dashboard | `uvicorn backend.api:app` |

Run notebooks in a fresh project kernel after `uv sync --extra notebooks --extra agents`. The optional Gradio dashboard is available with `uv sync --extra gradio` then `uv run python app.py`.

## Tests

```bash
uv run pytest -q
uv run --extra notebooks python -m examples.validate_notebooks
cd frontend && npm run build
```

See [VALIDATION.md](VALIDATION.md) for what has actually been tested. API-backed notebook cells are tagged `live` and excluded from offline execution.

## Architecture and limitations

```text
Agent runner → Trader agents → Accounts MCP → SQLite
                      ├──────→ Market MCP → fixtures / synthetic / prior close
                      ├──────→ Summary MCP → local log (optional notification)
                      └──────→ Researcher tool → Fetch / Search / Memory MCP
SQLite → FastAPI → TypeScript dashboard
```

This is a local prototype. One worker owns each persona; account updates are not safe for concurrent writers to the same account. MCP resources are not authenticated tenant boundaries. Dashboard metrics from the fixture demo are synthetic examples, not investment results. Live model behavior and optional third-party integrations need their own end-to-end validation.

## Attribution

Adapted from MIT-licensed MCP application code by Ed Donner. See [ATTRIBUTION.md](ATTRIBUTION.md) and [LICENSE](LICENSE) for provenance and the project-specific changes. Community contributions are excluded.
