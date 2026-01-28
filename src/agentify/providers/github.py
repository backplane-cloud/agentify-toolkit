from dotenv import load_dotenv
import os
import requests

def run_github(model_id: str, user_prompt: str) -> str:
    
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
    header = {
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
        ]
    }

    response = requests.post(url, json=body, headers=header)
    response.raise_for_status()

    data = response.json()
    return data["choices"][0]["message"]["content"]
