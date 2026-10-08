"""Simulation personas shared by the API, dashboards and agent runner."""
import os
from . import settings
names = ["Value", "Macro", "Balanced", "Innovation"]
lastnames = ["Fundamentals", "Macro signals", "Diversification", "Technology"]
model_names = [os.environ.get("TRADER_MODEL", "gpt-4o-mini")] * 4
short_model_names = ["Scripted demo"] * 4 if os.environ.get("MARKET_MODE") == "fixture" else model_names.copy()
STRATEGIES = {
    "Value": "In this simulation, compare company fundamentals before making small paper positions.",
    "Macro": "In this simulation, study macroeconomic news and explain each paper position.",
    "Balanced": "In this simulation, favor diversification and avoid concentrated paper positions.",
    "Innovation": "In this simulation, research technology businesses and document uncertainty.",
}
