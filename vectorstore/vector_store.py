# chromadb/vector_store.py

import chromadb
from chromadb.config import Settings
from typing import List, Dict

# 기본 Chroma 설정 (로컬 DB 경로 등)
import chromadb

client = chromadb.PersistentClient(path="chromadb_store")
collection = client.get_or_create_collection("documents")

def add_documents(docs: List[Dict]):
    """
    docs: {"id": str, "text": str, "metadata": dict} 형태의 리스트
    """
    ids = [doc["id"] for doc in docs]
    texts = [doc["text"] for doc in docs]
    metadatas = [doc.get("metadata", {}) for doc in docs]

    collection.add(
        ids=ids,
        documents=texts,
        metadatas=metadatas
    )


def query_top_k(query: str, k: int = 3) -> List[Dict]:
    """
    유사한 문서 top-k 검색
    """
    results = collection.query(
        query_texts=[query],
        n_results=k
    )

    return [
        {
            "id": results["ids"][0][i],
            "text": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i]
        }
        for i in range(len(results["ids"][0]))
    ]