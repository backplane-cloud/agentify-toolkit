from openai import OpenAI
from dotenv import load_dotenv
import os

from .rate_card import estimate_cost

def run_openai(model_id: str, user_prompt: str) -> str:
    load_dotenv()
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Missing OPENAI_API_KEY environment variable. "
            "Please set it in your shell or in a .env file."
            "Use Command: agentify provider add openai"

        )
    
    client = OpenAI(api_key=api_key)

    response = client.responses.create(
        model=model_id,
        input=user_prompt
    )

    input_tokens = response.usage.input_tokens
    output_tokens = response.usage.output_tokens
    token_cost = estimate_cost("openai", model_id, input_tokens, output_tokens)

    result = {
        "text": response.output_text,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "token_cost": token_cost
    }
    
    return result
