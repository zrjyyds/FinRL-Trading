"""动量因子。"""

from __future__ import annotations

import pandas as pd


def compute_momentum(prices: pd.DataFrame, lookback_days: int = 20) -> pd.DataFrame:
    """动量因子（Momentum Factor）。

    零基础解释：动量因子用过去一段时间涨跌幅衡量资产强弱。
    """

    df = prices.copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["ticker", "date"])
    df[f"momentum_{lookback_days}d"] = df.groupby("ticker")["close"].pct_change(lookback_days)
    return df


def rank_momentum(momentum_df: pd.DataFrame, date: str, lookback_days: int = 20) -> pd.DataFrame:
    col = f"momentum_{lookback_days}d"
    day = pd.Timestamp(date)
    rows = momentum_df[pd.to_datetime(momentum_df["date"]) == day][["ticker", col]].dropna().copy()
    if rows.empty:
        return pd.DataFrame(columns=["ticker", col, "momentum_rank_score"])
    rows["rank"] = rows[col].rank(method="first")
    if len(rows) == 1:
        rows["momentum_rank_score"] = 1.0
    else:
        rows["momentum_rank_score"] = (rows["rank"] - 1) / (len(rows) - 1)
    return rows.sort_values("momentum_rank_score", ascending=False).reset_index(drop=True)
