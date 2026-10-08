"""Activity-summary MCP tool; local log by default, optional Pushover delivery."""
import os
import requests
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP
from .database import write_log
mcp = FastMCP("activity_summary")
class PushModelArgs(BaseModel):
    message: str = Field(min_length=1, max_length=2000, description="A brief activity summary")

@mcp.tool()
def push(args: PushModelArgs) -> str:
    """Record a simulation summary locally; deliver only if ENABLE_PUSH is explicitly enabled."""
    write_log("system", "summary", args.message)
    if os.environ.get("ENABLE_PUSH", "false").lower() != "true":
        return "Summary recorded locally; external delivery disabled."
    token, user = os.getenv("PUSHOVER_TOKEN"), os.getenv("PUSHOVER_USER")
    if not token or not user:
        raise ValueError("Pushover delivery requires PUSHOVER_TOKEN and PUSHOVER_USER")
    response = requests.post("https://api.pushover.net/1/messages.json", data={"token": token, "user": user, "message": args.message}, timeout=15)
    response.raise_for_status()
    if response.json().get("status") != 1:
        raise RuntimeError("Pushover did not confirm delivery")
    return "Summary recorded and delivered."

if __name__ == "__main__":
    mcp.run(transport="stdio")
