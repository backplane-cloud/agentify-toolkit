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
        name: github
        description: This is an example Github Models agent
        version: 0.1.0
        model:
          provider: github
          id: openai/gpt-4.1
          api_key_env: GITHUB_API_KEY
        role: you are a github expert
        """)

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

  
