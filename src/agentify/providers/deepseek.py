from openai import OpenAI
from dotenv import load_dotenv
import os

from .rate_card import estimate_cost

def run_deepseek(model_id: str, user_prompt: str, stream: bool = False) -> dict:
    load_dotenv()
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Missing DEEPSEEK_API_KEY environment variable. "
            "Please set it in your shell or in a .env file."
            "Use Command: agentify provider add deepseek"

        )
    
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")

    messages = [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": user_prompt},
    ]

    if not stream:

        response = client.chat.completions.create(
            model=model_id,
            messages=messages,
        )
        
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        token_cost = estimate_cost("deepseek", model_id, input_tokens, output_tokens)

        return {
            "text": response.choices[0].message.content,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "token_cost": token_cost
        }
        

    # STREAMING
    from rich.console import Console
    console = Console()

    full_text = ""
    input_tokens = 0
    output_tokens = 0

    stream_resp = client.chat.completions.create(
        model=model_id,
        messages=messages,
        stream=True
    )

    for chunk in stream_resp:
        token = chunk.choices[0].delta.content or ""
        console.print(token, end="")
        full_text += token

        # usage appears in final chunk
        if chunk.usage:
            input_tokens = chunk.usage.prompt_tokens
            output_tokens = chunk.usage.completion_tokens

    console.print()

    token_cost = estimate_cost("deepseek", model_id, input_tokens, output_tokens)

    return {
        "text": full_text,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "token_cost": token_cost
    }
 