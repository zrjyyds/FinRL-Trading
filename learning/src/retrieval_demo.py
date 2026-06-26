"""离线 TF-IDF 检索演示。"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def retrieve_notes(path: str | Path, query: str, top_k: int = 3) -> pd.DataFrame:
    """词频-逆文档频率（Term Frequency-Inverse Document Frequency，TF-IDF）检索。

    零基础解释：TF-IDF 不是大语言模型嵌入，只是用词频帮助匹配查询和资料。
    """

    notes = pd.read_csv(path)
    texts = notes["text"].astype(str).tolist()
    vectorizer = TfidfVectorizer()
    matrix = vectorizer.fit_transform(texts)
    query_vec = vectorizer.transform([query])
    sims = cosine_similarity(query_vec, matrix).ravel()
    result = notes.copy()
    result["similarity"] = sims
    return result.sort_values("similarity", ascending=False).head(top_k).reset_index(drop=True)
