import pytest
from click.testing import CliRunner
from agentify.cli import main
from pathlib import Path
import textwrap


def test_run_agent_yaml(tmp_path):
    runner = CliRunner()

    # Create a temporary agent.yaml file
    example_yaml = tmp_path / "agent.yaml"
    example_yaml.write_text(textwrap.dedent("""
name: claude
description: AI Engineer
version: 0.1.0
model:
  provider: anthropic
  id: claude-sonnet-4-5
  api_key_env: ANTHROPIC_API_KEY
role: |
  You are an AI Security Engineer.
  Provide concise, practical answers with examples.

"""))

    # Invoke CLI command with input
    user_input="echo hello"
    result = runner.invoke(main, ["run", str(example_yaml)], input=user_input)
    # Check output
    assert "hello" in result.output
    
    # # Invoke CLI command with input
    # user_input = "/exit"
    # result = runner.invoke(main, ["run", str(example_yaml)], input=user_input)
    # # Check exit code
    # assert result.exit_code == 0

  
