"""Project-local paths and configuration; loading settings never calls an API."""
import os
from pathlib import Path
from dotenv import load_dotenv
ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env", override=False)
DATA_DIR = Path(os.environ.get("MCP_DATA_DIR", str(ROOT / "artifacts"))).resolve()
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "accounts.db"
