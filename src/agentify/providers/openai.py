from openai import OpenAI
from dotenv import load_dotenv
import os

def run_openai(model_id: str, user_prompt: str) -> str:
    load_dotenv()
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Missing OPENAI_API_KEY environment variable. "
            "Please set it in your shell or in a .env file."
        )
    
    client = OpenAI(api_key=api_key)

    response = client.responses.create(
        model=model_id,
        input=user_prompt
    )
    return response.output_text