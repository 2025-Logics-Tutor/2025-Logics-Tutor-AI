# gpt_service.py

from openai import AsyncOpenAI
from typing import AsyncGenerator, List, Dict
from config.settings import Settings

settings = Settings()
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

class GPTService:

    async def stream_chat(self, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            stream=True,
            temperature=0.7
        )
        async for chunk in response:
            delta = chunk.choices[0].delta.content or ""
            if delta:
                yield delta
