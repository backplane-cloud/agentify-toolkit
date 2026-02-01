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
name: bedrock
description: AWS Bedrock Agent
version: 0.1.0
model:
  provider: bedrock
  id: anthropic.claude-3-sonnet-20240229-v1:0
  api_key_env: BEDROCK_API_KEY
role: |
  You are an AWS Cloud Architect. 
  Provide concise, practical answers.
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

  
