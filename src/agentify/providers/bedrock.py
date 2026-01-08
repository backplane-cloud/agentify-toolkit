import boto3
import json

def run_bedrock(model_id: str, user_prompt: str, config: dict = None) -> str:
        client = boto3.client(
            service_name="bedrock-runtime",
            region_name="eu-west-1"
        )

        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "temperature": 0.2,
            "messages": [
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
        }

        response = client.invoke_model(
            modelId=model_id,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json"
        )

        response_body = json.loads(response["body"].read())
        return response_body["content"][0]["text"]