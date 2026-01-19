from mistralai import Mistral
from dotenv import load_dotenv
import os

def run_mistral(model_id: str, user_prompt: str) -> str:
    load_dotenv()
    api_key = os.environ["MISTRAL_API_KEY"]
    if not api_key:
        raise RuntimeError(
            "Missing MISTRAL_API_KEY environment variable. "
            "Please set it in your shell or in a .env file."
        )
    client = Mistral(api_key=api_key)

    response = client.chat.complete(
        model= model_id,
        messages = [
            {
                "role": "user",
                "content": user_prompt,
            },
        ]
    )
    return response.choices[0].message.content