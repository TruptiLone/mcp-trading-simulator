"""Bounded paper-trading rounds. Default: one round, never an endless scheduler."""
import argparse
import asyncio
from .profiles import names, lastnames, model_names, short_model_names

def create_traders():
    from .traders import Trader
    return [Trader(name, label, model) for name, label, model in zip(names, lastnames, model_names)]

async def run_rounds(rounds=1, interval=60):
    if rounds < 1 or interval < 0:
        raise ValueError("rounds must be positive and interval nonnegative")
    from agents import add_trace_processor
    from .tracers import LogTracer
    add_trace_processor(LogTracer())
    traders = create_traders()
    for index in range(rounds):
        results = await asyncio.gather(*(trader.run() for trader in traders), return_exceptions=True)
        failures = [str(result) for result in results if isinstance(result, Exception)]
        if failures:
            raise RuntimeError("One or more agents failed: " + "; ".join(failures))
        if index < rounds - 1:
            await asyncio.sleep(interval)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rounds", type=int, default=1)
    parser.add_argument("--interval", type=float, default=60, help="Seconds between rounds")
    args = parser.parse_args()
    asyncio.run(run_rounds(args.rounds, args.interval))

if __name__ == "__main__":
    main()
