from ollama import Client
from dotenv import load_dotenv
import os

def run_ollama(model_id: str, user_prompt: str) -> str:
    load_dotenv()
    api_key = os.environ.get("OLLAMA_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Missing OLLAMA_API_KEY environment variable. "
            "Please set it in your shell or in a .env file."
        )
    
    client = Client(
        host="https://ollama.com",
        headers={'Authorization': 'Bearer ' + api_key}
    )

    messages = [
        {
            'role': 'user',
            'content': user_prompt,
        },
    ]

    response =  client.chat(model_id, messages=messages, stream=False)
    return response.message.content

   




