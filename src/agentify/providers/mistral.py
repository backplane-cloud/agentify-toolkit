import os
from mistralai import Mistral



def run_mistral(model_id: str, user_prompt: str) -> str:
    api_key = os.environ["MISTRAL_API_KEY"]
    client = Mistral(api_key=api_key)

    response = client.chat.complete(
        model= model_id,
        messages = [
            {
                "role": "user",
                "content": user_prompt,
            },
        ]
    )
    return response.choices[0].message.content