import math
import pytest
from backend.accounts import Account
from backend import accounts

@pytest.mark.parametrize("quantity", [0, -1, 1.5, True])
def test_invalid_orders_do_not_mutate_account(quantity):
    account = Account.get("Test")
    original = account.model_dump()
    with pytest.raises(ValueError):
        account.buy_shares("AAPL", quantity, "invalid")
    with pytest.raises(ValueError):
        account.sell_shares("AAPL", quantity, "invalid")
    assert account.model_dump() == original

@pytest.mark.parametrize("amount", [0, -10, float("nan"), float("inf"), True])
def test_invalid_cash_flows(amount):
    account = Account.get("Test")
    with pytest.raises(ValueError): account.deposit(amount)
    with pytest.raises(ValueError): account.withdraw(amount)
    assert account.balance == 10000

@pytest.mark.parametrize("price", [0, -1, float("nan"), float("inf")])
def test_invalid_quotes_do_not_mutate_account(monkeypatch, price):
    monkeypatch.setattr(accounts, "get_share_price", lambda symbol: price)
    account = Account.get("Test")
    with pytest.raises(ValueError): account.buy_shares("AAPL", 1, "invalid quote")
    assert not account.transactions
    assert account.balance == 10000

def test_roundtrip_pnl_and_persistence():
    account = Account.get("Test")
    account.buy_shares(" aapl ", 10, "fixture")
    assert account.balance == pytest.approx(8998)
    account = Account.get("TEST")
    assert account.holdings == {"AAPL": 10}
    account.sell_shares("AAPL", 10, "fixture")
    assert account.holdings == {}
    assert account.get_profit_loss() == pytest.approx(-4)
    assert account.balance == pytest.approx(9996)

def test_cash_flows_are_not_profit():
    account = Account.get("Test")
    account.deposit(1000)
    account.withdraw(500)
    assert account.get_profit_loss() == 0
    account = Account.get("test")
    assert account.net_deposits == 500
    account.reset()
    assert account.net_deposits == 0

def test_insufficient_cash_and_holdings():
    account = Account.get("Test")
    with pytest.raises(ValueError): account.buy_shares("AAPL", 1000, "too much")
    with pytest.raises(ValueError): account.sell_shares("AAPL", 1, "none owned")
    with pytest.raises(ValueError): account.withdraw(10001)
    assert account.balance == 10000
