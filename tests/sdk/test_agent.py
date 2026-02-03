from agentify import Agent

def test_agent_run():

    # Arrange
    agent = Agent(
        name="buzz",
        description="AI Security Architect",
        provider="google",
        model_id="gemini-2.5-flash",
        role="cloud-architect"
    )

    # Act
    response = agent.run("In 3 words what is your provider and name")

    # Assert
    assert isinstance(response, str) # Response is a string
    assert "google" in response.lower() # Contains provider