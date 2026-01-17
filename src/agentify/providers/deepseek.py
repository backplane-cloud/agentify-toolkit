# Please install OpenAI SDK first: `pip3 install openai`
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY'), base_url="https://api.deepseek.com/v1")

def run_deepseek(model_id: str, user_prompt: str) -> str:

    response = client.chat.completions.create(
        model=model_id,
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": user_prompt},
        ],
        stream=False
    )

    return (response.choices[0].message.content)

 
from openai import OpenAI

def run_openai(model_id: str, user_prompt: str) -> str:
    client = OpenAI()

    response = client.responses.create(
        model=model_id,
        input=user_prompt
    )
    return response.output_text