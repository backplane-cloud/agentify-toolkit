from anthropic import Anthropic
from dotenv import load_dotenv
import os

from .rate_card import estimate_cost

def run_anthropic(model_id: str, user_prompt: str) -> str:
    load_dotenv()
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Missing ANTHROPIC_API_KEY environment variable. "
            "Please set it in your shell or in a .env file."
            "Use Command: agentify provider add anthropic"
        )
    
    client = Anthropic(api_key=api_key) 
     
    message = client.messages.create(
        model= model_id,
        max_tokens=1024,
        messages=[
            {
                "role": "user", 
                "content": user_prompt
            }
        ]
    )

    input_tokens = message.usage.input_tokens
    output_tokens = message.usage.output_tokens
    token_cost = estimate_cost(model_id, input_tokens, output_tokens)

    result = {
        "text": message.content[0].text,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "token_cost": token_cost
    }
    return result




 
  