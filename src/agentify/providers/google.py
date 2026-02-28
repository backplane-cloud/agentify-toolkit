from google import genai
from dotenv import load_dotenv
import os

from .rate_card import estimate_cost

def run_google(model_id: str, user_prompt: str) -> str:
    load_dotenv()
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Missing GOOGLE_API_KEY environment variable. "
            "Please set it in your shell or in a .env file."
            "Use Command: agentify provider add google"

        )   
    
    client = genai.Client()
    response = client.models.generate_content(
        model=model_id,
        contents=user_prompt
    )

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

