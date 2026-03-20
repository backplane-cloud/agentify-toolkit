from mistralai import Mistral
from dotenv import load_dotenv
import os

from .rate_card import estimate_cost

def run_mistral(model_id: str, user_prompt: str, stream: bool = False) -> dict:
    load_dotenv()
    api_key = os.environ["MISTRAL_API_KEY"]
    if not api_key:
        raise RuntimeError(
            "Missing MISTRAL_API_KEY environment variable. "
            "Please set it in your shell or in a .env file."
            "Use Command: agentify provider add mistral"

        )
    client = Mistral(api_key=api_key)

    messages = [
        {
            "role": "user",
            "content": user_prompt,
        },
    ]

    if not stream:
        response = client.chat.complete(
            model= model_id,
            messages = messages
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
    # STREAMING
    else:
        from rich.console import Console
        console = Console()

        full_text = ""
        input_tokens = 0
        output_tokens = 0

        stream_resp = client.chat.stream(
            model=model_id,
            messages=messages
        )

        for chunk in stream_resp:
            if chunk.data.choices:
                token = chunk.data.choices[0].delta.content or ""
                console.print(token, end="")
                full_text += token

        console.print()

        # After streaming, request usage info via a normal call
        # (Mistral streaming does not include usage in chunks)
        response = client.chat.complete(
            model=model_id,
            messages=messages
        )

        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens

        token_cost = estimate_cost("mistral", model_id, input_tokens, output_tokens)

        return {
            "text": full_text,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "token_cost": token_cost
        }