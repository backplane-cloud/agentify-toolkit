# Copyright 2026 Backplane Software
# Licensed under the Apache License, Version 2.0

from agentify import Agent
import os

def create_agents(specs: list) -> dict[str, Agent]:
    agents = {}
    for spec in specs:
        agent = create_agent(spec)
        agents[agent.name] = agent
    return agents

def create_agent(spec: dict, provider: str = None, model: str = None) -> Agent:
    """
    Create an Agent from a YAML/spec dictionary, optionally overriding model or provider.
    """
    name = spec.get("name")
    description = spec.get("description")
    version = spec.get("version")
    role = spec.get("role")

    model_spec = spec.get("model", {})
    model_id = model or model_spec.get("id")
    provider = provider or model_spec.get("provider")
    api_key_env = model_spec.get("api_key_env")

    if api_key_env:
        api_key = os.getenv(api_key_env)
    # if not api_key:
    #     raise EnvironmentError(
    #         f"Environment variables '{api_key_env}' is not set"
    #     )
    
    # Collect extra config
    model_config = {k: v for k, v in model_spec.items() if k not in ["id", "provider", "api_key_env"]}
    
    agent = Agent(name=name, provider=provider, model_id=model_id, role=role, description=description, version=version, model_config=model_config)

    return agent
