import os
from xai_sdk import Client
from xai_sdk.chat import user, system

def run_x(model_id: str, user_prompt: str) -> str:
    client = Client()
    chat = client.chat.create(model=model_id)
    chat.append(system("You are Grok, a highly intelligent, helpful AI assistant."))
    chat.append(user(user_prompt))
    response = chat.sample()

    return response.content