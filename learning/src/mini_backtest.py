"""独立教学回测器。"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class BacktestResult:
    equity_curve: pd.DataFrame
    daily_weights: pd.DataFrame
    trades: pd.DataFrame
    total_turnover: float


def _validate_targets(target_weights: pd.DataFrame) -> None:
    if (target_weights["weight"] < -1e-12).any():
        raise ValueError("target weights must be non-negative")
    sums = target_weights.groupby("execution_date")["weight"].sum()
    if (sums > 1.000001).any():
        raise ValueError("target weight sum must not exceed 1")


def run_backtest(
    prices: pd.DataFrame,
    target_weights: pd.DataFrame,
    initial_cash: float = 10000.0,
    transaction_cost: float = 0.001,
    slippage: float = 0.0005,
) -> BacktestResult:
    """回测（Backtesting）。

    零基础解释：回测用历史数据模拟策略规则过去会怎样表现，不代表未来一定赚钱。
    """

    px = prices.copy()
    px["date"] = pd.to_datetime(px["date"])
    px = px.sort_values(["date", "ticker"])
    targets = target_weights.copy()
    if targets.empty:
        targets = pd.DataFrame(columns=["execution_date", "ticker", "weight"])
    targets["execution_date"] = pd.to_datetime(targets["execution_date"])
    _validate_targets(targets)

    tickers = sorted(px["ticker"].unique())
    shares = {ticker: 0.0 for ticker in tickers}
    cash = float(initial_cash)
    equity_rows = []
    weight_rows = []
    trade_rows = []
    total_turnover = 0.0

    for day, day_prices in px.groupby("date"):
        day_prices = day_prices.set_index("ticker")
        if day in set(targets["execution_date"]):
            before_value = cash + sum(shares[t] * float(day_prices.loc[t, "open"]) for t in tickers)
            day_target = targets[targets["execution_date"] == day].set_index("ticker")["weight"].to_dict()
            turnover_value = 0.0
            for ticker in tickers:
                target_w = float(day_target.get(ticker, 0.0))
                open_px = float(day_prices.loc[ticker, "open"])
                current_value = shares[ticker] * open_px
                target_value = before_value * target_w
                diff_value = target_value - current_value
                if abs(diff_value) < 1e-9:
                    continue
                side = "buy" if diff_value > 0 else "sell"
                exec_px = open_px * (1.0 + slippage if side == "buy" else 1.0 - slippage)
                delta_shares = diff_value / exec_px
                notional = abs(delta_shares * exec_px)
                fee = notional * transaction_cost
                shares[ticker] += delta_shares
                cash -= delta_shares * exec_px
                cash -= fee
                turnover_value += notional
                trade_rows.append(
                    {
                        "date": day.strftime("%Y-%m-%d"),
                        "ticker": ticker,
                        "side": side,
                        "shares": delta_shares,
                        "price": exec_px,
                        "notional": notional,
                        "fee": fee,
                    }
                )
            if before_value > 0:
                total_turnover += turnover_value / before_value

        close_value = cash + sum(shares[t] * float(day_prices.loc[t, "close"]) for t in tickers)
        holding_value = close_value - cash
        equity_rows.append(
            {
                "date": day.strftime("%Y-%m-%d"),
                "equity": close_value,
                "cash": cash,
                "holding_value": holding_value,
            }
        )
        for ticker in tickers:
            value = shares[ticker] * float(day_prices.loc[ticker, "close"])
            weight_rows.append(
                {
                    "date": day.strftime("%Y-%m-%d"),
                    "ticker": ticker,
                    "weight": value / close_value if close_value > 0 else np.nan,
                }
            )

    return BacktestResult(
        equity_curve=pd.DataFrame(equity_rows),
        daily_weights=pd.DataFrame(weight_rows),
        trades=pd.DataFrame(trade_rows),
        total_turnover=float(total_turnover),
    )
