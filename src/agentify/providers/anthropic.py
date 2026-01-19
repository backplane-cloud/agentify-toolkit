from anthropic import Anthropic
from dotenv import load_dotenv
import os

def run_anthropic(model_id: str, user_prompt: str) -> str:
    load_dotenv()
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Missing ANTHROPIC_API_KEY environment variable. "
            "Please set it in your shell or in a .env file."
        )
    
    client = Anthropic(api_key=api_key) 
     
    message = client.messages.create(
        model= model_id,
        max_tokens=1024,
        messages=[
            {
                "role": "user", 
                "content": user_prompt
            }
        ]
    )
    return message.content[0].text