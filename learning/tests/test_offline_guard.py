import socket

import pandas as pd

from learning.src.mock_llm_provider import MockLLMProvider
from learning.src.sample_data import generate_news
from learning.src.sentiment_factor import classify_news


def test_learning_code_does_not_open_network(monkeypatch):
    def blocked(*args, **kwargs):
        raise AssertionError("network access is forbidden in learning tests")

    monkeypatch.setattr(socket, "create_connection", blocked)
    monkeypatch.setattr(socket.socket, "connect", blocked)

    news = generate_news().head(5)
    result = classify_news(news, MockLLMProvider())
    assert len(result) == 5
    assert set(result["provider"]) == {"offline_mock"}
