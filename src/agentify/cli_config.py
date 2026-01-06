import json
from pathlib import Path

CONFIG_PATH = Path.home() / ".agentify" / "config.json"

def load_config():
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text())
    return {}

def save_config(config: dict):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(config, indent=2))

def set_server(url: str):
    config = load_config()
    config["server_url"] = url
    save_config(config)
    print(f"Default server set to {url}")

def get_server(default=None):
    config = load_config()
    return config.get("server_url", default)
