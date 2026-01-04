 
from openai import OpenAI

def run_openai(model_id: str, user_prompt: str) -> str:
    client = OpenAI()

    response = client.responses.create(
        model=model_id,
        input=user_prompt
    )
    return response.output_text