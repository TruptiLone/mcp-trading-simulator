from pydantic import BaseModel
import json
import math
import re
from dotenv import load_dotenv
from datetime import datetime
from .market import get_share_price
from .database import write_account, read_account, write_log



INITIAL_BALANCE = 10_000.0
SPREAD = 0.002


class Transaction(BaseModel):
    symbol: str
    quantity: int
    price: float
    timestamp: str
    rationale: str

    def total(self) -> float:
        return self.quantity * self.price

    def __repr__(self):
        return f"{abs(self.quantity)} shares of {self.symbol} at {self.price} each."


class Account(BaseModel):
    name: str
    balance: float
    net_deposits: float = 0.0
    strategy: str
    holdings: dict[str, int]
    transactions: list[Transaction]
    portfolio_value_time_series: list[tuple[str, float]]

    @classmethod
    def get(cls, name: str):
        fields = read_account(name.lower())
        if not fields:
            fields = {
                "name": name.lower(),
                "balance": INITIAL_BALANCE,
                "strategy": "",
                "holdings": {},
                "transactions": [],
                "portfolio_value_time_series": []
            }
            write_account(name, fields)
        return cls(**fields)


    def save(self):
        write_account(self.name.lower(), self.model_dump())

    def reset(self, strategy: str=""):
        self.net_deposits = 0.0
        self.balance = INITIAL_BALANCE
        self.strategy = strategy
        self.holdings = {}
        self.transactions = []
        self.portfolio_value_time_series = []
        self.save()

    def deposit(self, amount: float):
        """ Deposit funds into the account. """
        if isinstance(amount, bool) or not math.isfinite(amount) or amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        self.balance += amount
        self.net_deposits += amount

        self.save()

    def withdraw(self, amount: float):
        """ Withdraw funds from the account, ensuring it doesn't go negative. """
        if isinstance(amount, bool) or not math.isfinite(amount) or amount <= 0:
            raise ValueError("Withdrawal amount must be finite and positive.")
        if amount > self.balance:
            raise ValueError("Insufficient funds for withdrawal.")
        self.balance -= amount
        self.net_deposits -= amount

        self.save()

    def buy_shares(self, symbol: str, quantity: int, rationale: str) -> str:
        """ Buy shares of a stock if sufficient funds are available. """
        symbol = self._validate_order(symbol, quantity)
        price = self._validate_price(get_share_price(symbol))
        buy_price = price * (1 + SPREAD)
        total_cost = buy_price * quantity

        if total_cost > self.balance:
            raise ValueError("Insufficient funds to buy shares.")
        elif price==0:
            raise ValueError(f"Unrecognized symbol {symbol}")

        # Update holdings
        self.holdings[symbol] = self.holdings.get(symbol, 0) + quantity
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Record transaction
        transaction = Transaction(symbol=symbol, quantity=quantity, price=buy_price, timestamp=timestamp, rationale=rationale)
        self.transactions.append(transaction)

        # Update balance
        self.balance -= total_cost
        self.save()
        write_log(self.name, "account", f"Bought {quantity} of {symbol}")
        return "Completed. Latest details:\n" + self.report()

    def sell_shares(self, symbol: str, quantity: int, rationale: str) -> str:
        """ Sell shares of a stock if the user has enough shares. """
        symbol = self._validate_order(symbol, quantity)
        if self.holdings.get(symbol, 0) < quantity:
            raise ValueError(f"Cannot sell {quantity} shares of {symbol}. Not enough shares held.")

        price = self._validate_price(get_share_price(symbol))
        sell_price = price * (1 - SPREAD)
        total_proceeds = sell_price * quantity

        # Update holdings
        self.holdings[symbol] -= quantity

        # If shares are completely sold, remove from holdings
        if self.holdings[symbol] == 0:
            del self.holdings[symbol]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Record transaction
        transaction = Transaction(symbol=symbol, quantity=-quantity, price=sell_price, timestamp=timestamp, rationale=rationale)  # negative quantity for sell
        self.transactions.append(transaction)

        # Update balance
        self.balance += total_proceeds
        self.save()
        write_log(self.name, "account", f"Sold {quantity} of {symbol}")
        return "Completed. Latest details:\n" + self.report()

    def calculate_portfolio_value(self):
        """ Calculate the total value of the user's portfolio. """
        total_value = self.balance
        for symbol, quantity in self.holdings.items():
            total_value += get_share_price(symbol) * quantity
        return total_value

    def calculate_profit_loss(self, portfolio_value: float):
        """ Calculate profit or loss from the initial spend. """
        return portfolio_value - INITIAL_BALANCE - self.net_deposits

    @staticmethod
    def _validate_order(symbol: str, quantity: int) -> str:
        if type(quantity) is not int or quantity <= 0:
            raise ValueError("Quantity must be a positive whole number")
        symbol = symbol.strip().upper()
        if not re.fullmatch(r"[A-Z][A-Z0-9.-]{0,9}", symbol):
            raise ValueError("Invalid ticker symbol")
        return symbol

    @staticmethod
    def _validate_price(price: float) -> float:
        if not math.isfinite(price) or price <= 0:
            raise ValueError("Quote must be finite and positive")
        return price

    def get_holdings(self):
        """ Report the current holdings of the user. """
        return self.holdings

    def get_profit_loss(self):
        """ Report the user's profit or loss at any point in time. """
        return self.calculate_profit_loss(self.calculate_portfolio_value())

    def list_transactions(self):
        """ List all transactions made by the user. """
        return [transaction.model_dump() for transaction in self.transactions]

    def report(self) -> str:
        """ Return a json string representing the account.  """
        portfolio_value = self.calculate_portfolio_value()
        self.portfolio_value_time_series.append((datetime.now().strftime("%Y-%m-%d %H:%M:%S"), portfolio_value))
        self.save()
        pnl = self.calculate_profit_loss(portfolio_value)
        data = self.model_dump()
        data["total_portfolio_value"] = portfolio_value
        data["total_profit_loss"] = pnl
        write_log(self.name, "account", "Retrieved account details")
        return json.dumps(data)

    def get_strategy(self) -> str:
        """ Return the strategy of the account """
        write_log(self.name, "account", "Retrieved strategy")
        return self.strategy

    def change_strategy(self, strategy: str) -> str:
        """ At your discretion, if you choose to, call this to change your investment strategy for the future """
        self.strategy = strategy
        self.save()
        write_log(self.name, "account", "Changed strategy")
        return "Changed strategy"
