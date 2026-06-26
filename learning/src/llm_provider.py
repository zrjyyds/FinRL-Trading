"""大语言模型提供商接口。"""

from __future__ import annotations

from datetime import datetime
from typing import Protocol

from .schemas import SentimentResult


class BaseLLMProvider(Protocol):
    """大语言模型提供商（LLM Provider）。

    零基础解释：Provider 是负责接收文本并返回模型结果的组件。
    """

    provider_name: str
    model_name: str

    def analyze_sentiment(self, text: str, ticker: str, published_at: datetime) -> SentimentResult:
        ...
