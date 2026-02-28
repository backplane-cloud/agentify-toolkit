from xai_sdk import Client
from xai_sdk.chat import user, system
from dotenv import load_dotenv
import os

from .rate_card import estimate_cost

def run_x(model_id: str, user_prompt: str) -> str:
    load_dotenv()
    api_key = os.environ.get("XAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Missing XAI_API_KEY environment variable. "
            "Please set it in your shell or in a .env file."
            "Use Command: agentify provider add xai"

        )
    
    client = Client(api_key=api_key)
    chat = client.chat.create(model=model_id)
    chat.append(system("You are Grok, a highly intelligent, helpful AI assistant."))
    chat.append(user(user_prompt))
    response = chat.sample()
    
    input_tokens = response.usage.prompt_tokens + response.usage.reasoning_tokens
    output_tokens = response.usage.completion_tokens
    token_cost = estimate_cost("xai", model_id, input_tokens, output_tokens)

    result = {
        "text": response.content,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "token_cost": token_cost
    }
    return result

