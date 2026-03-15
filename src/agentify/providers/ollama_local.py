
import requests
import json
from rich.console import Console

def run_ollama_local(model_id: str, user_prompt: str, stream: bool = False) -> dict:
    """
    Run a local Ollama model.
    Supports streaming output if stream=True.
    """
    console = Console()
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model_id,
        "prompt": user_prompt,
        "stream": stream
    }

    if stream:
        # Streaming mode
        with requests.post(url, json=payload, stream=True) as resp:
            resp.raise_for_status()
            full_text = ""
            input_tokens = 0
            output_tokens = 0

            for line in resp.iter_lines(decode_unicode=True):
                if not line:
                    continue
                try:
                    chunk = json.loads(line)
                except json.JSONDecodeError:
                    continue

                # The model's incremental text
                token = chunk.get("response", "")
                console.print(token, end="")
                full_text += token

                # Update token counts if present (likely only on final chunk)
                input_tokens = chunk.get("prompt_eval_count", input_tokens)
                output_tokens = chunk.get("eval_count", output_tokens)

            console.print()  # newline after streaming
    else:
        # Non-streaming mode
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        full_text = data["response"]
        input_tokens = data.get("prompt_eval_count", 0)
        output_tokens = data.get("eval_count", 0)

    token_cost = 0  # local models are free for now; optionally use rate card

    return {
        "text": full_text,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "token_cost": token_cost
    }
   




