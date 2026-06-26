"""可选 OpenAI 兼容接口，默认关闭。"""

from __future__ import annotations

import json
import os
from datetime import datetime

from pydantic import ValidationError

from .schemas import SentimentResult


class OpenAICompatibleProvider:
    """OpenAI 兼容接口（OpenAI-Compatible API）。

    零基础解释：它使用类似 OpenAI SDK 的格式连接模型服务。本阶段默认禁用。
    """

    def __init__(self, enabled: bool = False, timeout: float = 15.0, max_tokens: int = 120, temperature: float = 0.0):
        self.enabled = enabled
        self.timeout = timeout
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.provider_name = "openai_compatible"
        self.model_name = os.getenv("LEARNING_LLM_MODEL", "disabled")

    def analyze_sentiment(self, text: str, ticker: str, published_at: datetime) -> SentimentResult:
        if not self.enabled:
            raise RuntimeError("OpenAICompatibleProvider is disabled in offline learning mode")

        api_key = os.getenv("LEARNING_LLM_API_KEY")
        base_url = os.getenv("LEARNING_LLM_BASE_URL")
        model = os.getenv("LEARNING_LLM_MODEL")
        if not api_key or not model:
            raise RuntimeError("LEARNING_LLM_API_KEY and LEARNING_LLM_MODEL are required when enabled")

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("openai package is not installed; install requirements-learning-online.txt explicitly") from exc

        client = OpenAI(api_key=api_key, base_url=base_url, timeout=self.timeout) if base_url else OpenAI(api_key=api_key, timeout=self.timeout)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Return strict JSON for sentiment only."},
                {"role": "user", "content": text},
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content or "{}"
        try:
            payload = json.loads(content)
            payload.update(
                {
                    "ticker": ticker,
                    "published_at": published_at,
                    "provider": self.provider_name,
                    "model_name": model,
                }
            )
            return SentimentResult(**payload)
        except (json.JSONDecodeError, ValidationError) as exc:
            raise RuntimeError(f"model returned invalid structured output: {exc}") from exc
