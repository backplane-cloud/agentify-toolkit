from dotenv import load_dotenv
import os
import requests
import json

import tiktoken  # official OpenAI tokenizer, lightweight and fast
from rich.console import Console

from .rate_card import estimate_cost

def run_github(model_id: str, user_prompt: str, stream: bool = False) -> dict:
    
    # Get Api Key
    load_dotenv()
    api_key = os.environ.get("GITHUB_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Missing GITHUB_API_KEY environment variable. "
            "Please set it in your shell or in a .env file."
            "Use Command: agentify provider add github"
        )

    # Create Request header and body
    url = "https://models.github.ai/inference/chat/completions"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {api_key}",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json"
    }
    body = {
        "model": model_id,
        "messages": [
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        "stream": stream
    }

    provider, model = model_id.split("/") 

    # Initialize the tokenizer for this model
    enc = tiktoken.encoding_for_model(model)

    # NON-STREAMING
    if not stream:
        response = requests.post(url, json=body, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        input_tokens = data["usage"]["prompt_tokens"]
        output_tokens = data["usage"]["completion_tokens"]
        token_cost = estimate_cost(provider, model, input_tokens, output_tokens)

        result = {
            "text": data["choices"][0]["message"]["content"],
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "token_cost": token_cost
        }
        return result

    # STREAMING
    from rich.console import Console
    console = Console()

    full_text = ""
    input_tokens = 0
    output_tokens = 0

    response = requests.post(url, json=body, headers=headers, stream=True)
    response.raise_for_status()

    for line in response.iter_lines():

        if not line:
            continue

        decoded = line.decode("utf-8").strip()

        if not decoded.startswith("data:"):
            continue

        payload = decoded.replace("data: ", "")

        if payload == "[DONE]":
            break

        try:
            chunk = json.loads(payload)
        except json.JSONDecodeError:
            continue  # skip invalid JSON

        # Safely get streaming token content
        choices = chunk.get("choices", [])
        if choices:
            delta = choices[0].get("delta", {})
            token = delta.get("content")
            if token:
                console.print(token, end="")
                full_text += token
                output_tokens += len(enc.encode(token))

    # Count input tokens from the prompt
    input_tokens = len(enc.encode(user_prompt))
    token_cost = estimate_cost(provider, model, input_tokens, output_tokens)

    return {
        "text": full_text,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "token_cost": token_cost
    }