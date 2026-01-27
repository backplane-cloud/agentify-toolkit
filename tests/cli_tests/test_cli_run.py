import pytest
from click.testing import CliRunner
from agentify.cli import main
from pathlib import Path

def test_run_agent_yaml(tmp_path):
    runner = CliRunner()

    # Create a temporary agent.yaml file
    example_yaml = tmp_path / "agent.yaml"
    example_yaml.write_text(
"""
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

    user_input = "/exit\n"

    # Invoke CLI command with input
    result = runner.invoke(main, ["run", str(example_yaml)], input=user_input)

    # Check exit code
    assert result.exit_code == 0

    # Check output
    assert "Using claude-sonnet-4-5 by anthropic" in result.output
