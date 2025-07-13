from chromadb import Client
from sentence_transformers import SentenceTransformer

# 전역 초기화
chroma_client = Client()
collection = chroma_client.get_or_create_collection("asklogic_docs")
embedder = SentenceTransformer("all-MiniLM-L6-v2")

def retrieve_documents(question: str, k: int = 3) -> list[str]:
    query_embedding = embedder.encode(question).tolist()
    results = collection.query(query_embeddings=[query_embedding], n_results=k)
    return results["documents"][0]
