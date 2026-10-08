"""Run one bounded MCP researcher invocation; requires agents extra and a model key."""
import argparse
import asyncio
import os
from contextlib import AsyncExitStack

async def research(question):
    from backend import settings
    from backend.mcp_servers import researcher_mcp_servers
    from backend.traders import get_researcher
    from agents import Runner
    async with AsyncExitStack() as stack:
        servers = [await stack.enter_async_context(server) for server in researcher_mcp_servers("ResearchDemo")]
        agent = await get_researcher(servers, os.environ.get("TRADER_MODEL", "gpt-4o-mini"))
        result = await Runner.run(agent, question, max_turns=12)
        print(result.final_output)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("question", help="Research question, ideally with a source URL when Tavily is not configured")
    asyncio.run(research(parser.parse_args().question))
