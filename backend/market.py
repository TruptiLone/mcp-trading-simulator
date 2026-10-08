"""Explicit fixture, simulated or live quote modes; never silently mix sources."""
import math
import os
from . import settings
from .market_simulator import simulated_price
MODE = os.environ.get("MARKET_MODE", "simulated").lower()
if MODE not in {"fixture", "simulated", "live"}:
    raise ValueError("MARKET_MODE must be fixture, simulated or live")
massive_api_key = os.environ.get("MASSIVE_API_KEY") if MODE == "live" else None
FIXTURE_PRICES = {"AAPL": 100.0, "MSFT": 200.0, "NVDA": 50.0, "SPY": 400.0}

def get_share_price(symbol: str) -> float:
    symbol = symbol.strip().upper()
    if MODE == "fixture":
        if symbol not in FIXTURE_PRICES:
            raise ValueError(f"No fixture price for {symbol}")
        price = FIXTURE_PRICES[symbol]
    elif MODE == "simulated":
        price = simulated_price(symbol)
    else:
        if not massive_api_key:
            raise RuntimeError("MARKET_MODE=live requires MASSIVE_API_KEY")
        from massive import RESTClient
        price = float(RESTClient(massive_api_key).get_previous_close_agg(symbol)[0].close)
    if not math.isfinite(price) or price <= 0:
        raise ValueError("Quote must be finite and positive")
    return price

def is_market_open() -> bool:
    if MODE != "live":
        return True
    if not massive_api_key:
        raise RuntimeError("MARKET_MODE=live requires MASSIVE_API_KEY")
    from massive import RESTClient
    return RESTClient(massive_api_key).get_market_status().market == "open"
