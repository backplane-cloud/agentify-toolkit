# tests/cli_tests/test_cli_provider.py
import pytest
from click.testing import CliRunner
from agentify.cli import main

def test_provider_list():
    runner = CliRunner()

    # Run the CLI 'provider list' command
    result = runner.invoke(main, ["provider", "list"])

    # Check that CLI ran successfully
    assert result.exit_code == 0

    # Optionally check for expected provider names (depending on your default providers)
    expected_providers = ["openai", "anthropic", "google", "bedrock", "xai", "deepseek", "mistral", "ollama"]
    for provider in expected_providers:
        assert provider in result.output
