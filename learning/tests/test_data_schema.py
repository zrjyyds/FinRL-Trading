import pandas as pd

from learning.src.market_data import validate_price_data
from learning.src.sample_data import generate_news, generate_prices
from learning.src.schemas import NewsSchema, PriceSchema


def test_price_schema_and_ohlcv_rules():
    prices = generate_prices()
    validate_price_data(prices)
    assert len(prices["ticker"].unique()) == 5
    assert prices.groupby("ticker").size().min() == 300
    PriceSchema(**prices.iloc[0].to_dict())


def test_news_schema_and_labels():
    news = generate_news()
    assert len(news) >= 150
    assert set(news["expected_label"]) == {"positive", "neutral", "negative"}
    NewsSchema(**news.iloc[0].to_dict())
    parsed = pd.to_datetime(news["available_at"], utc=True) >= pd.to_datetime(news["published_at"], utc=True)
    assert parsed.all()
