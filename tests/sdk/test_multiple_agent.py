from agentify import Agent

def test_multiple_runs_are_independent():
    agent1 = Agent(
        name="buzz",
        description="AI Security Architect",
        provider="google",
        model_id="gemini-2.5-flash",
        role="cloud-architect"
    )

    agent2 = Agent(
        name="buzz",
        description="AI Security Architect",
        provider="google",
        model_id="gemini-2.5-flash",
        role="cloud-architect"
    )

    agent1 = agent1.run("Say apple")
    agent2 = agent2.run("Say banana")

    assert "apple" in agent1.lower()
    assert "banana" in agent2.lower()
