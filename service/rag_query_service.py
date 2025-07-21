# service/rag_query_service.py

from service.embedding_service import embed_text
from vectorstore.vector_store import query_top_k
from typing import List, Dict, Tuple

from typing import List, Dict
from service.embedding_service import embed_text
from vectorstore.vector_store import query_top_k
from model.schema import Level

def get_system_prompt(level: Level, with_context: bool, context: str = "") -> str:
    if with_context:
        return (
            "너는 사용자의 질문에 성실하게 답변하는 논리학 튜터야.\n"
            "가능한 경우 아래 문맥(Context)을 기반으로만 답변해야 해.\n"
            "문맥이 충분하지 않다면, '잘 모르겠다'고 말해줘. 추측하지 마!\n\n"
            f"💡 설명 대상 수준: {level.name}\n"
            f"[문맥 Context]\n{context}"
        )
    else:
        return {
            Level.ELEMENTARY: (
                "너는 **초등학생**에게 설명하는 친절한 논리학 튜터야.\n"
                "어려운 용어나 기호는 피하고, 아주 쉽게 풀어서 설명해줘."
            ),
            Level.UNIV: (
                "너는 **대학생**에게 설명하는 논리학 튜터야.\n"
                "핵심 개념을 정확히 전달하고, 예시를 통해 이해를 도와줘."
            ),
            Level.GRAD: (
                "너는 **대학원생**에게 설명하는 전문 논리학 튜터야.\n"
                "깊이 있는 개념 설명과 논리적 근거, 예시를 포함해서 설명해줘."
            )
        }[level]

from typing import List, Dict
from vectorstore.vector_store import query_top_k
from model.schema import Level


def get_system_prompt(level: Level) -> str:
    return {
        Level.ELEMENTARY: "너는 초등학생에게 설명해주는 친절한 논리학 튜터야. 쉬운 말로 풀어서 설명해줘.",
        Level.UNIV: "너는 대학생에게 설명해주는 논리학 튜터야. 핵심 개념을 정확하게 전달해줘.",
        Level.GRAD: "너는 대학원생에게 설명해주는 전문 논리학 튜터야. 깊이 있는 설명과 예시를 포함해줘."
    }[level]

async def build_rag_messages(
        user_message: str,
        history: List[Dict[str, str]],
        level: Level,
        quote: str | None = None
) -> Tuple[List[Dict[str, str]], bool]:
    top_k_results = query_top_k(user_message, k=3)

    # 🔧 유사도 거리 기준 문서 기반 여부 결정
    threshold = 0.7  # 이 값보다 거리 작으면 is_documented = True
    most_relevant_distance = top_k_results[0]["distance"] if top_k_results else None
    is_documented = most_relevant_distance is not None and most_relevant_distance < threshold

    # ✅ quote 포함된 전체 질문 생성
    if quote:
        full_user_message = f'다음 내용을 인용해서 질문할게:\n"""\n{quote}\n"""\n\n{user_message}'
    else:
        full_user_message = user_message

    # ✅ 시스템 프롬프트 구성
    if is_documented:
        context = "\n\n---\n\n".join([doc["text"] for doc in top_k_results])
        system_prompt = (
            "너는 사용자의 질문에 성실하게 대답하는 논리학 튜터야.\n"
            "가능한 경우 아래 문맥(Context)을 참고해서 대답하고,\n"
            "문맥이 부족하거나 관련 없으면 대화 흐름(history)과 네 지식에 따라 친절히 설명해줘.\n\n"
            f"[문맥 Context]\n{context}"
        )
    else:
        system_prompt = get_system_prompt(level)

    # ✅ 로그 출력
    print("🔎 RAG 검색 대상 메시지:", user_message)
    print("🔎 검색 결과 개수:", len(top_k_results))
    for i, doc in enumerate(top_k_results):
        preview = doc["text"].strip().replace("\n", " ")[:40]
        print(f"  [{i}] 내용: {preview} / 거리: {doc['distance']:.4f}")
    print("📌 is_documented:", is_documented)

    # ✅ 메시지 구성
    messages = [{"role": "system", "content": system_prompt}] + history + [
        {"role": "user", "content": full_user_message}
    ]

    return messages, is_documented
