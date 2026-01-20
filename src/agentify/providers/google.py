from google import genai
from dotenv import load_dotenv
import os

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

    return response.text