# Copyright Backplane 2026
# Author: Lewis Sheridan
# License: MIT
# Description: Simple Demo to use Agentify Library to create an AI Agent

from agentify import Agent

def main():

    # Open AI Agent
    # agent = Agent(
    #     name="OpenAI Agent", 
    #     description="OpenAI's GPT Agent",
    #     provider="OpenAI", 
    #     model_id="gpt-5-nano", 
    #     role="You are an AI Security Architect specialising in OpenAI models" 
    # )

    # Google Gemini Agent
    # agent = Agent(
    #     name="Gemini Agent", 
    #     description="Google's Gemini Agent",
    #     provider="Google", 
    #     model_id="gemini-2.5-flash", 
    #     role="You are an AI Security Architect specialising in Google's models" 
    # )

    # Anthropic Claude Agent
    # agent = Agent(
    #     name="Anthropic", 
    #     description="Anthropic's Claude Sonnet Agent",
    #     provider="Anthropic", 
    #     model_id="claude-sonnet-4-5", 
    #     role="You are an AI Security Architect specialising in Anthropic's models" 
    # )

    # X's Grok Agent
    agent = Agent(
        name="Grok", 
        version="0.1.0",
        description="X's Grok Agent",
        provider="x", 
        model_id="grok-4", 
        role="You are an AI Security Architect specialising in X AI Grok models" 
    )

    agent.chat()
    
if __name__ == "__main__":
    main()