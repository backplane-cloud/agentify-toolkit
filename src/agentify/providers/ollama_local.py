
import requests
import json

def run_ollama_local(model_id: str, user_prompt: str) -> str:
    
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model_id,
        "prompt": user_prompt,
        "stream": False
    }

    response = requests.post(url, json=payload)

    response.raise_for_status()

    data = response.json()
    return data["response"]

   




