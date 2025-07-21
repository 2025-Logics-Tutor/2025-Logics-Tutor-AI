# test_query.py

from vectorstore.vector_store import query_top_k

query = "기호 논리학의 구성 요소는?"
results = query_top_k(query)

for doc in results:
    print(f"🔎 유사도: {doc['distance']:.4f}")
    print(f"📄 문서 내용: {doc['text']}\n")
