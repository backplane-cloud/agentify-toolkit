from openai import OpenAI

def run_docker(model_id: str, user_prompt: str, config: dict = None) -> str:
    if config is None:
        config = {}
    base_url = config.get("base_url", "http://localhost:12434/v1")
    client = OpenAI(
        base_url=base_url,
        api_key="dummy"  # Not needed for local
    )

    response = client.responses.create(
        model=model_id,
        input=user_prompt
    )
    return response.output_text