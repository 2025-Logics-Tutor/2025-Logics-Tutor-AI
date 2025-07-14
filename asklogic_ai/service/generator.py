import json

import openai
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI  # ✅ 새로운 클라이언트 방식

load_dotenv()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def stream_answer(prompt: str):
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        stream=True,
    )

    async for chunk in response:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

async def generate_conversation_response(prompt: str) -> dict:
    system_prompt = (
        "아래의 사용자의 질문에 대해 답변을 생성해 주세요.\n"
        "- 먼저 주제(title)를 한 줄로 요약해 주세요.\n"
        "- 그 후 전체 답변(answer)를 이어서 작성해 주세요.\n"
        "- 모든 응답은 반드시 JSON 형식으로 아래와 같이 반환해 주세요:\n\n"
        "{\n  \"title\": \"주제를 요약한 한 문장\",\n  \"answer\": \"자세한 답변 내용\"\n}\n"
    )

    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"질문: {prompt}"}
        ],
        temperature=0.2
    )

    raw_content = response.choices[0].message.content.strip()

    try:
        json_start = raw_content.index("{")
        json_data = json.loads(raw_content[json_start:])
        return {
            "title": json_data.get("title", "제목 없음"),
            "answer": json_data.get("answer", "")
        }
    except Exception as e:
        return {
            "title": "파싱 오류",
            "answer": f"응답 파싱 중 오류 발생: {str(e)}\n\n원본 응답: {raw_content}"
        }
