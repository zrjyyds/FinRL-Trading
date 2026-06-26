"""市场数据读取与校验。"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

REQUIRED_PRICE_COLUMNS = ["date", "ticker", "open", "high", "low", "close", "volume"]


def load_price_data(path: str | Path) -> pd.DataFrame:
    """读取开盘价、最高价、最低价、收盘价和成交量（Open, High, Low, Close and Volume，OHLCV）。

    零基础解释：OHLCV 是一天市场数据的基础格式。
    """

    df = pd.read_csv(path)
    validate_price_data(df)
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values(["date", "ticker"]).reset_index(drop=True)


def validate_price_data(df: pd.DataFrame) -> None:
    missing = [col for col in REQUIRED_PRICE_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"missing price columns: {missing}")
    if df[REQUIRED_PRICE_COLUMNS].isna().any().any():
        raise ValueError("price data contains missing required fields")
    if df.duplicated(["date", "ticker"]).any():
        raise ValueError("price data contains duplicated date/ticker rows")
    for col in ["open", "high", "low", "close"]:
        if (df[col] <= 0).any():
            raise ValueError(f"{col} must be positive")
    if (df["volume"] <= 0).any():
        raise ValueError("volume must be positive")
    if (df["high"] < df[["open", "close", "low"]].max(axis=1)).any():
        raise ValueError("high must be no lower than open, close, and low")
    if (df["low"] > df[["open", "close", "high"]].min(axis=1)).any():
        raise ValueError("low must be no higher than open, close, and high")
