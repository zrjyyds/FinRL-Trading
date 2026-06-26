from datetime import datetime

import pytest
from pydantic import ValidationError

from learning.src.schemas import SentimentResult


def test_sentiment_result_validates_ranges():
    result = SentimentResult(
        label="positive",
        score=0.5,
        confidence=0.8,
        reason="ok",
        ticker="aaa",
        published_at=datetime.now(),
        provider="mock",
        model_name="rules",
    )
    assert result.ticker == "AAA"


def test_sentiment_result_rejects_invalid_label():
    with pytest.raises(ValidationError):
        SentimentResult(
            label="bullish",
            score=2.0,
            confidence=1.2,
            reason="bad",
            ticker="AAA",
            published_at=datetime.now(),
            provider="mock",
            model_name="rules",
        )
