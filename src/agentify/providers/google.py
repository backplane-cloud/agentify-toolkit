from google import genai
from dotenv import load_dotenv
import os
import tiktoken

from .rate_card import estimate_cost

def run_google(model_id: str, user_prompt: str, stream: bool = False) -> dict:
    load_dotenv()
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Missing GOOGLE_API_KEY environment variable. "
            "Please set it in your shell or in a .env file."
            "Use Command: agentify provider add google"

        )   
    
    client = genai.Client()

    # tokenizer (fallback to cl100k if model unknown)
    try:
        enc = tiktoken.encoding_for_model(model_id)
    except Exception:
        enc = tiktoken.get_encoding("cl100k_base")

    # ---------- NON STREAMING ----------       

    if not stream:
        response = client.models.generate_content(
            model=model_id,
            contents=user_prompt
        )

        text = response.text

        input_tokens = response.usage_metadata.candidates_token_count + response.usage_metadata.prompt_token_count
        output_tokens = response.usage_metadata.thoughts_token_count

        token_cost = estimate_cost("google", model_id, input_tokens, output_tokens)

        result = {
            "text": response.text,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "token_cost": token_cost
        }
        return result

    # ---------- STREAMING ----------
    from rich.console import Console
    console = Console()

    full_text = ""
    first_chunk = True
    is_json = False
    output_tokens = 0

    stream_resp = client.models.generate_content_stream(
        model=model_id,
        contents=user_prompt
    )

    for chunk in stream_resp:

        token = chunk.text or ""

        if not token:
            continue

        # Detect JSON tool invocation
        if first_chunk:
            is_json = token.lstrip().startswith("{")
            first_chunk = False

        if not is_json:
            console.print(token, end="")

        full_text += token

        # token estimation
        output_tokens += len(enc.encode(token))

    console.print()

    input_tokens = len(enc.encode(user_prompt))

    token_cost = estimate_cost("google", model_id, input_tokens, output_tokens)

    return {
        "text": full_text,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "token_cost": token_cost
    }
