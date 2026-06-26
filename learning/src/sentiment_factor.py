"""情绪因子。"""

from __future__ import annotations

from datetime import datetime

import pandas as pd

from .mock_llm_provider import MockLLMProvider
from .time_alignment import filter_available_news


def classify_news(news: pd.DataFrame, provider: MockLLMProvider | None = None) -> pd.DataFrame:
    """情绪因子（Sentiment Factor）。

    零基础解释：情绪因子把新闻的正面、中性、负面结果转成数字。
    """

    llm = provider or MockLLMProvider()
    rows = []
    for _, row in news.iterrows():
        published = pd.Timestamp(row["published_at"]).to_pydatetime()
        result = llm.analyze_sentiment(f"{row['title']}\n{row['body']}", row["ticker"], published)
        rows.append({**row.to_dict(), **result.model_dump()})
    return pd.DataFrame(rows)


def daily_sentiment_factor(news_with_sentiment: pd.DataFrame, signal_timestamp: str | datetime) -> pd.DataFrame:
    usable = filter_available_news(news_with_sentiment, signal_timestamp)
    if usable.empty:
        return pd.DataFrame(columns=["date", "ticker", "sentiment_score"])
    usable["date"] = pd.to_datetime(usable["available_at"], utc=True).dt.tz_convert("America/New_York").dt.date
    grouped = usable.groupby(["date", "ticker"], as_index=False)["score"].mean()
    return grouped.rename(columns={"score": "sentiment_score"})


def rolling_sentiment_factor(daily: pd.DataFrame, window: int = 5) -> pd.DataFrame:
    if daily.empty:
        return daily.assign(rolling_sentiment=pd.Series(dtype=float))
    df = daily.copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["ticker", "date"])
    df["rolling_sentiment"] = (
        df.groupby("ticker")["sentiment_score"]
        .rolling(window, min_periods=1)
        .mean()
        .reset_index(level=0, drop=True)
    )
    return df
