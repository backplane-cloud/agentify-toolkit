import os
import getpass
import click
from pathlib import Path

ENV_FILE = Path(".env")
ENV_EXAMPLE_FILE = Path(".env.example")

PROVIDER_ENV_MAP = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
    "mistral": "MISTRAL_API_KEY",
    "xai": "XAI_API_KEY",
    "google": "GOOGLE_API_KEY",
    "bedrock": "BEDROCK_API_KEY",
}

def list_providers():
    """
    Returns a dict of provider -> (status, value mask)
    """
    results = {p: ("unset", None) for p in PROVIDER_ENV_MAP}

    if not ENV_FILE.exists():
        return results

    lines = ENV_FILE.read_text().splitlines(keepends=False)

    for provider, env_key in PROVIDER_ENV_MAP.items():
        for line in lines:
            if line.startswith(env_key + "="):
                value = line.split("=", 1)[1]
                if value and value.strip():
                    masked = value[:4] + "****"
                    results[provider] = ("set", masked)
                break

    return results


def display_providers():
    providers = list_providers()

    click.echo("Configured Providers:")

    # compute max length for alignment
    max_len = max(len(p) for p in providers)

    for provider, (status, masked) in providers.items():
        name_aligned = provider.ljust(max_len)
        if status == "set":
            click.secho(f"  ✓ {name_aligned}  ({masked})", fg="green")
        else:
            click.secho(f"  • {name_aligned}  (unset)", fg="yellow")


def remove_provider(provider: str):
    """
    Removes a provider entry from the `.env` file.
    """
    provider = provider.lower()
    if provider not in PROVIDER_ENV_MAP:
        raise ValueError(f"Unknown provider '{provider}'")

    if not ENV_FILE.exists():
        print(".env does not exist — nothing to remove")
        return

    env_key = PROVIDER_ENV_MAP[provider]
    lines = ENV_FILE.read_text().splitlines(keepends=False)

    new_lines = [line for line in lines if not line.startswith(env_key + "=")]
    ENV_FILE.write_text("\n".join(new_lines) + "\n")
    print(f"✓ Removed {env_key} from .env")

def load_or_create_env() -> list[str]:
    """
    Returns a list of lines from `.env` (existing or created from .env.example).
    """
    if ENV_FILE.exists():
        return ENV_FILE.read_text().splitlines(keepends=False)

    # If no .env but .env.example exists → copy structure
    if ENV_EXAMPLE_FILE.exists():
        lines = ENV_EXAMPLE_FILE.read_text().splitlines(keepends=False)
    else:
        # fallback minimal format
        lines = [
            "OPENAI_API_KEY=",
            "ANTHROPIC_API_KEY=",
            "DEEPSEEK_API_KEY=",
            "MISTRAL_API_KEY=",
            "XAI_API_KEY=",
            "GOOGLE_API_KEY=",
            "BEDROCK_API_KEY=",
        ]

    # Write the new .env skeleton
    ENV_FILE.write_text("\n".join(lines) + "\n")
    return lines


def update_env_key(provider_env_key: str, api_key: str):
    """
    Updates the provider key inside `.env`. If the key does not exist, it is appended.
    """
    lines = load_or_create_env()
    updated = False
    new_lines = []

    for line in lines:
        if line.startswith(provider_env_key + "="):
            new_lines.append(f"{provider_env_key}={api_key}")
            updated = True
        else:
            new_lines.append(line)

    if not updated:
        # Append new key at end with a newline
        new_lines.append(f"{provider_env_key}={api_key}")

    # Write back to `.env`
    ENV_FILE.write_text("\n".join(new_lines) + "\n")


def set_provider_key(provider: str):
    """
    Main entry point: prompts the user for the key and updates `.env`.
    """
    provider = provider.lower()


    if provider not in PROVIDER_ENV_MAP:
        raise ValueError(f"Unknown provider '{provider}'")

    env_key = PROVIDER_ENV_MAP[provider]
    api_key = getpass.getpass(f"Enter value for {env_key}: ")

    if not api_key.strip():
        raise ValueError("API key cannot be empty.")

    update_env_key(env_key, api_key)

    print(f"✓ Updated {env_key} in .env")
