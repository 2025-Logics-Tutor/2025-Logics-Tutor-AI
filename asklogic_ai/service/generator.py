import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

async def generate_answer(prompt: str) -> str:
    response = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content.strip()
