# service/rag_query_service.py

from service.embedding_service import embed_text
from vectorstore.vector_store import query_top_k
from typing import List, Dict


from typing import List, Dict
from service.embedding_service import embed_text
from vectorstore.vector_store import query_top_k
from model.schema import Level

def get_system_prompt(level: Level, with_context: bool, context: str = "") -> str:
    if with_context:
        return (
            "You are a helpful assistant that answers the user's question based on the provided context.\n"
            "Answer only using the context. If the context is insufficient, say you don't know.\n\n"
            f"Level: {level.name}\n"
            f"Context:\n{context}"
        )
    else:
        return {
            Level.ELEMENTARY: "너는 초등학생에게 설명해주는 친절한 논리학 튜터야. 쉬운 말로 풀어서 설명해줘.",
            Level.UNIV: "너는 대학생에게 설명해주는 논리학 튜터야. 핵심 개념을 정확하게 전달해줘.",
            Level.GRAD: "너는 대학원생에게 설명해주는 전문 논리학 튜터야. 깊이 있는 설명과 예시를 포함해줘."
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


from typing import List, Dict, Tuple
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
    is_documented = bool(top_k_results)

    # ✅ quote 포함된 전체 질문 생성
    if quote:
        full_user_message = f'다음 내용을 인용해서 질문할게:\n"""\n{quote}\n"""\n\n{user_message}'
    else:
        full_user_message = user_message

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

    messages = [{"role": "system", "content": system_prompt}] + history + [
        {"role": "user", "content": full_user_message}
    ]

    return messages, is_documented
