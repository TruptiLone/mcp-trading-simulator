import os
import tempfile
import sqlite3
import pytest
_test_data = tempfile.TemporaryDirectory()
os.environ["MCP_DATA_DIR"] = _test_data.name
os.environ["MARKET_MODE"] = "fixture"
os.environ["ENABLE_PUSH"] = "false"
from backend import database

@pytest.fixture(autouse=True)
def empty_accounts():
    with sqlite3.connect(database.DB) as connection:
        connection.execute("DELETE FROM accounts")
        connection.execute("DELETE FROM logs")
    yield
