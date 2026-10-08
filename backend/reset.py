"""Explicitly reset only the four simulator accounts."""
from .accounts import Account
from .profiles import STRATEGIES

def reset_traders():
    for name, strategy in STRATEGIES.items():
        Account.get(name).reset(strategy)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--confirm", action="store_true", help="Erase existing simulation positions")
    args = parser.parse_args()
    if not args.confirm:
        parser.error("Use --confirm to reset the four simulation accounts")
    reset_traders()
