import boto3
import json
import tiktoken

from .rate_card import estimate_cost

def run_bedrock(model_id: str, user_prompt: str, stream: bool = False) -> dict:
        
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

        # tokenizer fallback
        try:
            enc = tiktoken.encoding_for_model(model_id)
        except Exception:
            enc = tiktoken.get_encoding("cl100k_base")

        # ---------- NON STREAM ----------
        if not stream:
            
            response = client.invoke_model(
                modelId=model_id,
                body=json.dumps(body),
                contentType="application/json",
                accept="application/json"
            )

            response_body = json.loads(response["body"].read().decode('utf-8'))
            
            text = response_body["content"][0]["text"]

            # Calculate Token usage
            usage = response_body.get("usage")
            input_tokens = usage.get("input_tokens", 0)
            output_tokens = usage.get("output_tokens", 0)
            token_cost = estimate_cost("bedrock", model_id, input_tokens, output_tokens)

            return {
                "text": text,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "token_cost": token_cost,
            }
            
        # ---------- STREAMING ----------
        from rich.console import Console
        console = Console()

        full_text = ""
        output_tokens = 0

        response = client.invoke_model_with_response_stream(
            modelId=model_id,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json"
        )

        stream = response.get("body")

        for event in stream:

            chunk = event.get("chunk")

            if not chunk:
                continue

            payload = json.loads(chunk["bytes"].decode())

            # Bedrock Anthropic streaming format
            if payload.get("type") == "content_block_delta":

                token = payload["delta"].get("text", "")

                if not token:
                    continue
             
                console.print(token, end="")
                full_text += token
                output_tokens += len(enc.encode(token))

        console.print()


        input_tokens = len(enc.encode(user_prompt))
        token_cost = estimate_cost("bedrock", model_id, input_tokens, output_tokens)

        return {
            "text": full_text,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "token_cost": token_cost
        }