from google import genai

def run_google(model_id: str, user_prompt: str) -> str:
    client = genai.Client()
    response = client.models.generate_content(
        model=model_id,
        contents=user_prompt
    )

    return response.text