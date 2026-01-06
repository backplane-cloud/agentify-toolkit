"""
Copyright 2026 Backplane Software
Author: Lewis Sheridan
License: Apache License, Version 2.0
Description: Lightweight Python toolkit to build multi-model AI agents.
"""

from .agentify import Agent
from .agents import create_agent, create_agents
from .specs import load_agent_specs
from .cli_ui import show_agent_menu

__all__ = [
    "Agent",
    "load_agent_specs",
    "create_agent",
    "create_agents",
    "show_agent_menu"
]
