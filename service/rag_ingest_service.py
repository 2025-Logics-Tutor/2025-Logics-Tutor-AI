# service/rag_ingest_service.py

from data.rag_preprocessor import load_csv, preprocess_dataframe
from service.embedding_service import embed_texts
from vectorstore.vector_store import query_top_k, add_documents
from typing import Literal
import logging


async def ingest_csv_to_vectorstore(
        file_path: str,
        source: Literal["csv", "pdf", "web"] = "csv"
) -> int:
    """
    CSV 파일을 로드 → 전처리 → 임베딩 → ChromaDB 저장
    """
    try:
        df = load_csv(file_path)
        df = preprocess_dataframe(df)
        texts = df["combined"].tolist()
        ids = df["id"].astype(str).tolist()
        embeddings = embed_texts(texts)

        # ChromaDB에 저장
        documents = []
        for _id, text, emb in zip(ids, texts, embeddings):
            documents.append({
                "id": _id,
                "text": text,
                "metadata": {"source": source}
            })

        add_documents(documents)

        logging.info(f"✅ {len(documents)}건 저장 완료")
        return len(documents)

    except Exception as e:
        logging.error(f"❌ 벡터 저장 실패: {e}")
        raise
