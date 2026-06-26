"""学习层结构化数据模型。"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


SentimentLabel = Literal["positive", "neutral", "negative"]


class SentimentResult(BaseModel):
    """情绪分析（Sentiment Analysis）结果。

    零基础解释：情绪分析把新闻文本分成 positive、neutral、negative。
    """

    label: SentimentLabel
    score: float = Field(ge=-1.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str = Field(min_length=1, max_length=240)
    ticker: str = Field(min_length=1, max_length=12)
    published_at: datetime
    provider: str = Field(min_length=1)
    model_name: str = Field(min_length=1)

    @field_validator("ticker")
    @classmethod
    def normalize_ticker(cls, value: str) -> str:
        return value.strip().upper()

    @field_validator("reason")
    @classmethod
    def clean_reason(cls, value: str) -> str:
        return value.strip()


class PriceSchema(BaseModel):
    """开盘价、最高价、最低价、收盘价和成交量（Open, High, Low, Close and Volume，OHLCV）。

    零基础解释：OHLCV 是一天行情的五个基础字段。
    """

    date: str
    ticker: str
    open: float = Field(gt=0)
    high: float = Field(gt=0)
    low: float = Field(gt=0)
    close: float = Field(gt=0)
    volume: int = Field(gt=0)


class NewsSchema(BaseModel):
    """新闻样例数据模型。"""

    article_id: str
    ticker: str
    published_at: datetime
    available_at: datetime
    title: str
    body: str
    source: str
    expected_label: SentimentLabel

    @field_validator("available_at")
    @classmethod
    def available_not_before_publish(cls, value: datetime, info):
        published_at = info.data.get("published_at")
        if published_at is not None and value < published_at:
            raise ValueError("available_at must be later than or equal to published_at")
        return value
