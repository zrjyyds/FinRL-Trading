import pandas as pd

from learning.src.mini_backtest import run_backtest
from learning.src.sample_data import generate_prices


def _targets(prices):
    dates = sorted(prices["date"].unique())
    return pd.DataFrame(
        [
            {"execution_date": dates[30], "ticker": "AAA", "weight": 0.5},
            {"execution_date": dates[30], "ticker": "BBB", "weight": 0.5},
            {"execution_date": dates[60], "ticker": "CCC", "weight": 0.5},
            {"execution_date": dates[60], "ticker": "DDD", "weight": 0.5},
        ]
    )


def test_costs_and_slippage_reduce_equity():
    prices = generate_prices()
    targets = _targets(prices)
    no_cost = run_backtest(prices, targets, transaction_cost=0.0, slippage=0.0)
    fee = run_backtest(prices, targets, transaction_cost=0.001, slippage=0.0)
    slip = run_backtest(prices, targets, transaction_cost=0.001, slippage=0.0005)
    assert fee.equity_curve["equity"].iloc[-1] <= no_cost.equity_curve["equity"].iloc[-1]
    assert slip.equity_curve["equity"].iloc[-1] <= fee.equity_curve["equity"].iloc[-1]


def test_zero_rebalance_has_zero_fees():
    prices = generate_prices()
    result = run_backtest(prices, pd.DataFrame(columns=["execution_date", "ticker", "weight"]))
    assert result.trades.empty
    assert result.total_turnover == 0.0
