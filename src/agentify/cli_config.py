import json
import yaml
from pathlib import Path

AGENTIFY_DIR = Path.home() / ".agentify"
CONFIG_PATH = Path.home() / ".agentify" / "config.json"
PROVIDERS_FILE = AGENTIFY_DIR / "providers.yaml"

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




# -----------------------------
# Provider config
# -----------------------------
def load_providers():
    """
    Load provider configuration from disk.

    Returns:
        dict: provider configuration
    """
    if not PROVIDERS_FILE.exists():
        return {}

    with open(PROVIDERS_FILE, "r") as f:
        return yaml.safe_load(f) or {}


def save_providers(data: dict):
    """
    Persist provider configuration to disk.
    """
    AGENTIFY_DIR.mkdir(parents=True, exist_ok=True)
    with open(PROVIDERS_FILE, "w") as f:
        yaml.safe_dump(data, f)


def add_provider(provider: str, env_var: str):
    """
    Register a provider and its environment variable.
    """
    provider = provider.lower()

    data = load_providers()
    data.setdefault("providers", {})
    data["providers"][provider] = {
        "env": env_var
    }

    save_providers(data)


def remove_provider(provider: str):
    """
    Remove a provider from configuration.

    Returns:
        str | None: env var name if provider existed
    """
    provider = provider.lower()
    data = load_providers()
    providers = data.get("providers", {})

    if provider not in providers:
        return None

    env_var = providers[provider]["env"]
    del providers[provider]
    save_providers(data)
    return env_var


def list_providers():
    """
    Return configured providers.

    Returns:
        dict
    """
    data = load_providers()
    return data.get("providers", {})