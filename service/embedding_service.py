# service/embedding_service.py

from sentence_transformers import SentenceTransformer
from typing import List

# ⚠️ 모델은 필요에 따라 변경 가능
model = SentenceTransformer("all-MiniLM-L6-v2")


def embed_text(text: str) -> List[float]:
    """
    단일 텍스트를 임베딩
    """
    return model.encode(text).tolist()


def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    여러 텍스트를 배치 임베딩
    """
    return model.encode(texts).tolist()
