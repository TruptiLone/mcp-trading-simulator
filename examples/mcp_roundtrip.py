"""Exercise a real stdio MCP server without an LLM or external network."""
import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run():
    root = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory() as data_dir:
        params = StdioServerParameters(command=sys.executable, args=["-m", "backend.accounts_server"], cwd=str(root), env={**os.environ, "MCP_DATA_DIR": data_dir, "MARKET_MODE": "fixture"})
        async with stdio_client(params) as streams:
            async with ClientSession(*streams) as session:
                await session.initialize()
                tools = await session.list_tools()
                assert {"get_balance", "get_holdings", "buy_shares", "sell_shares"} <= {tool.name for tool in tools.tools}
                result = await session.call_tool("buy_shares", {"name": "ProtocolDemo", "symbol": "AAPL", "quantity": 2, "rationale": "Protocol integration test"})
                assert not result.isError, result
                resource = await session.read_resource("accounts://accounts_server/ProtocolDemo")
                account = json.loads(resource.contents[0].text)
                assert account["holdings"]["AAPL"] == 2
                assert abs(account["balance"] - 9799.6) < 1e-6
                rejected = await session.call_tool("buy_shares", {"name": "ProtocolDemo", "symbol": "AAPL", "quantity": -1, "rationale": "Must be rejected"})
                assert rejected.isError
                print("MCP roundtrip passed: discover tools, buy, read resource, reject invalid order.")
                return {"tool_count": len(tools.tools), "balance": account["balance"], "invalid_order_rejected": True}

if __name__ == "__main__":
    asyncio.run(run())
