import pytest
from fastapi.testclient import TestClient
from backend.api import app, average_cost
from backend.accounts import Account
from backend import accounts

client = TestClient(app)

def test_roster_market_and_missing_trader():
    assert len(client.get("/api/traders").json()) == 4
    market = client.get("/api/market").json()
    assert market["source"] == "fixture"
    assert market["paper_trading"] is True
    assert client.get("/api/traders/unknown").status_code == 404

def test_log_limit_is_bounded():
    assert client.get("/api/traders/value/logs?last_n=-1").status_code == 422
    assert client.get("/api/traders/value/logs?last_n=201").status_code == 422

def test_read_endpoint_does_not_add_history():
    account = Account.get("Value")
    account.buy_shares("AAPL", 2, "fixture")
    before = len(Account.get("Value").portfolio_value_time_series)
    result = client.get("/api/traders/value")
    assert result.status_code == 200
    assert result.json()["holdings"][0]["quantity"] == 2
    assert len(Account.get("Value").portfolio_value_time_series) == before

def test_cost_basis_after_sell_and_rebuy(monkeypatch):
    account = Account.get("Value")
    account.buy_shares("AAPL", 10, "first buy")
    account.sell_shares("AAPL", 5, "partial sale")
    monkeypatch.setattr(accounts, "get_share_price", lambda symbol: 200)
    account.buy_shares("AAPL", 5, "second buy")
    assert average_cost(account, "AAPL") == pytest.approx(150.3)
