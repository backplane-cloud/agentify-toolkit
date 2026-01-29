import requests

def run_agentify(model_id: str, user_prompt: str) -> str:
    # Import providers
    from agentify.providers import run_openai, run_anthropic, run_google, run_bedrock, run_github, run_x, run_deepseek, run_mistral, run_ollama, run_ollama_local

    # Get the Provider and Model from model ID
    provider, model = model_id.split("/")

    # Run provider
    match provider.lower():
        case "openai":
            return run_openai(model, user_prompt)
        case "anthropic":
            return run_anthropic(model, user_prompt)
        case "google":
            return run_google(model, user_prompt)
        case "bedrock":
            return run_bedrock(model, user_prompt)
        case "github":
            return run_github(model, user_prompt)
        case "xai":
            return run_x(model, user_prompt)
        case "deepseek":
            return run_deepseek(model, user_prompt)
        case "mistral":
            return run_mistral(model, user_prompt)
        case "ollama":
            return run_ollama(model, user_prompt)
        case "ollama_local":
            return run_ollama_local(model, user_prompt)
        case _:
            raise ValueError(f"Unsupported provider: {provider}")
        
def run_gateway_http(model_id: str, user_prompt: str) -> str:
    response = requests.post(
        "http://127.0.0.1:8000/v1/chat",
        json={"model": model_id, "prompt": user_prompt},
        timeout=30
    )
    response.raise_for_status()
    return response.json()["response"]