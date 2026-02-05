# tests/cli_tests/test_cli_provider.py
from click.testing import CliRunner
from agentify.cli import main

def test_provider_validate():
    runner = CliRunner()

    # Simulate running:
    # agentify provider validate openai/gpt-4
    result = runner.invoke(
        main,
        ["provider", "validate", "openai/gpt-4"]
    )

    assert result.exit_code == 0
    assert "OPENAI/GPT-4_API_KEY validated" in result.output
