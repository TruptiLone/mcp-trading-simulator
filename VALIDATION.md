# Validation record

Validated locally on 2026-10-08 with Python 3.12 and Node 22.

- Python dependency resolution succeeded; uv.lock records the resolved environment.
- 22 pytest cases passed, including real MCP stdio discovery, a successful order, a resource read and invalid-order rejection.
- Account tests cover invalid quantities/cash flows/quotes, persistence, overspending, overselling, P&L and cash deposits.
- API tests cover four personas, quote mode, missing accounts, bounded log queries and cost basis after a partial sale/rebuy.
- All five notebook schemas and 19 code cells validated; 14 local cells executed successfully. 5 external/model cells were skipped with no fabricated outputs.
- TypeScript checking and the Vite production build passed.
- npm audit reported zero known vulnerabilities after updating Vite and affected transitive packages.
- A local browser check showed all four fixture portfolios, their positions, transactions and activity logs; theme switching worked, with no observed console errors. The narrow preview layout was corrected and showed no horizontal overflow at 329px.

Not executed: paid LLM agent rounds, Tavily, remote Context7, Qdrant, external memory-server integrations, Massive market data, Pushover delivery or the optional Gradio UI. Those paths are documented but not claimed as validated.

The fixture demo is scripted and uses synthetic prices. Its returns are not real investment performance.
