from openai import OpenAI
import requests
from typing import Optional


def _find_full_tag(base_url: str, model_id: str) -> Optional[str]:
    try:
        r = requests.get(f"{base_url}/models", timeout=5)
        r.raise_for_status()
        models = r.json()
        for m in models:
            tags = m.get("tags", []) or []
            for t in tags:
                if t.startswith(model_id + ":") or t == model_id:
                    return t
    except Exception:
        return None
    return None


def run_docker(model_id: str, user_prompt: str, config: dict = None) -> str:
    if config is None:
        config = {}
    # Allow either a full base_url or a host/port pair in the config
    base_url = config.get("base_url")
    if not base_url:
        port = config.get("port", 8080)
        host = config.get("host", "localhost")
        base_url = f"http://{host}:{port}"
    # Strip trailing '/v1' if provided (OpenAI client appends /v1)
    if base_url.endswith("/v1"):
        base_url = base_url[:-3]

    # First try using the OpenAI SDK compatibility (Responses API)
    try:
        client = OpenAI(base_url=base_url, api_key="dummy")
        resp = client.responses.create(model=model_id, input=user_prompt)
        return getattr(resp, "output_text", str(resp))
    except Exception:
        # Fall back to model-runner HTTP API
        pass

    # Resolve full model tag if available
    full_tag = _find_full_tag(base_url, model_id) or model_id

    # Try several engine endpoints until one works
    engines = ["llama.cpp", "llamacpp", "vllm", "openai"]
    for eng in engines:
        try:
            url = f"{base_url}/engines/{eng}/v1/chat/completions"
            payload = {
                "model": full_tag,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": user_prompt},
                ],
            }
            r = requests.post(url, json=payload, timeout=30)
            if r.status_code == 404:
                continue
            r.raise_for_status()
            data = r.json()
            # Expect OpenAI-style chat completion response
            choices = data.get("choices") or []
            if choices:
                msg = choices[0].get("message") or {}
                content = msg.get("content") or msg.get("text")
                if content:
                    return content
            # Fallback to other shapes
            if "output" in data:
                return data["output"]
            return str(data)
        except Exception:
            continue

    raise RuntimeError("Failed to contact Docker Model Runner on any known endpoint")