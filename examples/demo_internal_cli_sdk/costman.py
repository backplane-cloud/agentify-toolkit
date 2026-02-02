# Copyright Backplane 2026
# Author: Lewis Sheridan
# Description: Simple Demo to use Agentify Library to create an AI Agent

from agentify import Agent

def main():

    # Anthropic Claude Agent
    agent = Agent(
        name="Anthropic", 
        description="Anthropic's Claude Sonnet Agent",
        provider="Anthropic", 
        model_id="claude-sonnet-4-5", 
        role="You are an AI Security Architect specialising in Anthropic's models",
        tool_names=["random_user", "add_numbers"],
        agent_file=__file__,
    )

    agent.chat(debug=True)
    
if __name__ == "__main__":
    main()