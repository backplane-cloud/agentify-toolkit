from openai import OpenAI
from dotenv import load_dotenv
import os

from .rate_card import estimate_cost

def run_openai(model_id: str, user_prompt: str, stream=False) -> str:
    load_dotenv()
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Missing OPENAI_API_KEY environment variable. "
            "Please set it in your shell or in a .env file."
            "Use Command: agentify provider add openai"

        )
    
    client = OpenAI(api_key=api_key)

    if not stream:
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
    
    # STREAMING MODE

    full_text = ""
    from rich.console import Console
    console = Console()
    
    with client.responses.stream(
        model=model_id,
        input=user_prompt
    ) as stream:

        for event in stream:

            if event.type == "response.output_text.delta":
                console.print(event.delta, end="")
                full_text += event.delta

        final_response = stream.get_final_response()

        console.print()

        input_tokens = final_response.usage.input_tokens
        output_tokens = final_response.usage.output_tokens

        token_cost = estimate_cost("openai", model_id, input_tokens, output_tokens)

        return {
            "text": full_text,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "token_cost": token_cost
        }