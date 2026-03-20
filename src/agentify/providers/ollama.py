from ollama import Client
from dotenv import load_dotenv
import os

from .rate_card import estimate_cost


def run_ollama(model_id: str, user_prompt: str, stream: bool = False) -> str:
    load_dotenv()
    api_key = os.environ.get("OLLAMA_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Missing OLLAMA_API_KEY environment variable. "
            "Please set it in your shell or in a .env file."
            "Use Command: agentify provider add ollama"

        )
    
    client = Client(
        host="https://ollama.com",
        headers={'Authorization': f'Bearer {api_key}'}
    )

    messages = [{"role": "user", "content": user_prompt}]


    if not stream:
        response =  client.chat(model_id, messages=messages, stream=False)

        input_tokens = response.prompt_eval_count
        output_tokens = response.eval_count
        token_cost = estimate_cost("ollama", model_id, input_tokens, output_tokens)
        
        result = {
            "text": response.message.content,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "token_cost": token_cost

        }
        return result
    else: 
        # STREAMING
        full_text = ""
        from rich.console import Console
        console = Console()
        stream_resp = client.chat(model_id, messages=messages, stream=True)

        for partial in stream_resp:
            token = partial.message.content
            console.print(token, end="")
            full_text += token

            input_tokens = partial.prompt_eval_count
            output_tokens = partial.eval_count


    token_cost = estimate_cost("ollama", model_id, input_tokens, output_tokens)

    return {
        "text": full_text,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "token_cost": token_cost
    }




