from mistralai import Mistral
from dotenv import load_dotenv
import os

from .rate_card import estimate_cost

def run_mistral(model_id: str, user_prompt: str) -> str:
    load_dotenv()
    api_key = os.environ["MISTRAL_API_KEY"]
    if not api_key:
        raise RuntimeError(
            "Missing MISTRAL_API_KEY environment variable. "
            "Please set it in your shell or in a .env file."
            "Use Command: agentify provider add mistral"

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

    input_tokens = response.usage.prompt_tokens
    output_tokens = response.usage.completion_tokens
    token_cost = estimate_cost("mistral", model_id, input_tokens, output_tokens)

    result = {
        "text": response.choices[0].message.content,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "token_cost": token_cost
    }

    return result