import asyncio
from examples.mcp_roundtrip import run

def test_real_stdio_roundtrip():
    result = asyncio.run(run())
    assert result["tool_count"] >= 4
    assert result["invalid_order_rejected"]
