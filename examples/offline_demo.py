"""Generate deterministic paper-account data without any model or network calls."""
import argparse
import json
import os

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reset", action="store_true", help="Replace existing simulator account data")
    args = parser.parse_args()
    os.environ["MARKET_MODE"] = "fixture"
    from backend.accounts import Account
    from backend.profiles import STRATEGIES
    from backend.database import read_account
    from backend.settings import DATA_DIR
    if any(read_account(name) for name in STRATEGIES) and not args.reset:
        parser.error("Demo accounts already exist. Use --reset only to replace their data.")
    orders = {"Value": ("AAPL", 10), "Macro": ("MSFT", 5), "Balanced": ("SPY", 4), "Innovation": ("NVDA", 20)}
    report = {}
    for name, strategy in STRATEGIES.items():
        account = Account.get(name)
        account.reset(strategy)
        account.report()
        symbol, quantity = orders[name]
        account.buy_shares(symbol, quantity, "Deterministic fixture demo; no model decision")
        account.sell_shares(symbol, 1, "Exercise the simulated sell path")
        report[name] = json.loads(account.report())
    path = DATA_DIR / "demo_report.json"
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("Generated four fixture portfolios; no API calls. Report:", path)

if __name__ == "__main__":
    main()
