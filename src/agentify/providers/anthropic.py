from anthropic import Anthropic

def run_anthropic(model_id: str, user_prompt: str) -> str:
    client = Anthropic()  
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