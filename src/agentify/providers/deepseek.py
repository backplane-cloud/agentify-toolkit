from openai import OpenAI
from dotenv import load_dotenv
import os

def run_deepseek(model_id: str, user_prompt: str) -> str:
    load_dotenv()
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Missing DEEPSEEK_API_KEY environment variable. "
            "Please set it in your shell or in a .env file."
        )
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")

    response = client.chat.completions.create(
        model=model_id,
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": user_prompt},
        ],
        stream=False
    )

    return (response.choices[0].message.content)