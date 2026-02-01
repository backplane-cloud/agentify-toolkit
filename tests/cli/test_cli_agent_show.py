# tests/cli_tests/test_cli_agent.py
import pytest
from click.testing import CliRunner
from agentify.cli import main

def test_agent_show(tmp_path):
    runner = CliRunner()

    # Create a temporary agent.yaml file
    agent_file = tmp_path / "agent.yaml"
    agent_file.write_text("""
name: test-agent
description: A test agent
role: assistant
provider: anthropic
model:
  provider: anthropic
  id: claude-sonnet-4-5
  api_key_env: ANTHROPIC_API_KEY
tools: []
""")

    # Run the CLI command
    result = runner.invoke(main, ["agent", "show", str(agent_file)])

    # Check that CLI ran successfully
    assert result.exit_code == 0

    # Check that the output contains key fields
    assert "test-agent" in result.output
    assert "A test agent" in result.output
    assert "anthropic" in result.output
    assert "claude-sonnet-4-5" in result.output


