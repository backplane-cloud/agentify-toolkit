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
name: openai
description: OpenAI GPT Agent
version: 0.1.0
model:
  provider: openai
  id: gpt-5-nano
  api_key_env: OPEN_API_KEY
role: |
  You are an experienced cloud security engineer specialising in AWS.
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

  
