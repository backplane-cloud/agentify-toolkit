# tests/cli_tests/test_cli_provider.py
from click.testing import CliRunner
from agentify.cli import main

def test_provider_add():
    runner = CliRunner()

    # Simulate running:
    # agentify provider add ollama
    # Enter provider key: test-key-123
    result = runner.invoke(
        main,
        ["provider", "add", "ollama"],
        input="test-key-123\n"
    )

    assert result.exit_code == 0
    assert "Updated OLLAMA_API_KEY" in result.output
