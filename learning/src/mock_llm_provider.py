"""离线 Mock 大语言模型提供商。"""

from __future__ import annotations

import hashlib
from datetime import datetime

from .schemas import SentimentResult


class MockLLMProvider:
    """模拟提供商（Mock Provider）。

    零基础解释：Mock Provider 不联网、不收费，只按固定规则返回结果，不是真正的大语言模型。
    """

    provider_name = "offline_mock"
    model_name = "keyword-rules-v1"

    positive_keywords = ("stronger", "improved", "growth", "adoption", "retention", "订单增长", "成本改善", "产品进展")
    negative_keywords = ("softer", "delayed", "pressure", "risk", "uncertainty", "需求放缓", "成本压力", "执行风险")
    injection_keywords = ("ignore previous", "system override", "请忽略", "覆盖系统")

    def analyze_sentiment(self, text: str, ticker: str, published_at: datetime) -> SentimentResult:
        lowered = (text or "").lower()
        pos = sum(1 for key in self.positive_keywords if key.lower() in lowered)
        neg = sum(1 for key in self.negative_keywords if key.lower() in lowered)
        injected = any(key.lower() in lowered for key in self.injection_keywords)
        if injected:
            label = "negative"
            score = -0.4
            reason = "detected prompt-injection-like wording; treated cautiously"
        elif pos > neg:
            label = "positive"
            score = 0.7
            reason = "positive teaching keywords matched"
        elif neg > pos:
            label = "negative"
            score = -0.7
            reason = "negative teaching keywords matched"
        else:
            label = "neutral"
            score = 0.0
            reason = "no dominant teaching keyword matched"

        digest = int(hashlib.sha256(f"{ticker}|{text}".encode("utf-8")).hexdigest()[:6], 16)
        confidence = 0.55 + (digest % 35) / 100.0
        return SentimentResult(
            label=label,
            score=score,
            confidence=min(confidence, 0.9),
            reason=reason,
            ticker=ticker,
            published_at=published_at,
            provider=self.provider_name,
            model_name=self.model_name,
        )
