# tests/cli_tests/test_cli_agent.py
import pytest
from pathlib import Path

from click.testing import CliRunner
from agentify.cli import main

def test_agent_show(tmp_path):
    runner = CliRunner()

    # Path to agents
    path = Path(__file__).parent.parent.parent / "examples" / "agents"
    

    # Run the CLI command
    result = runner.invoke(main, ["agent", "list", str(path)])

    # Check that CLI ran successfully
    assert result.exit_code == 0

    # Check that the output contains key fields
    assert "snoopy" in result.output
    assert "anthropic" in result.output
    assert "claude-sonnet-4-5" in result.output


