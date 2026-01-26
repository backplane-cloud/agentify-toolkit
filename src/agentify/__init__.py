"""
Copyright 2026 Backplane Software
Author: Lewis Sheridan
License: Apache License, Version 2.0
Description: Lightweight Python toolkit to build multi-model AI agents.
"""
import os

try:
    from importlib.metadata import version, PackageNotFoundError

    try:
        __version__ = version("agentify-toolkit")
    except PackageNotFoundError:
        # Fallback when running locally from src/ (not installed)
        __version__ = "0.0.0-dev"
except ImportError:
    # Python <3.8 fallback
    __version__ = "0.0.0-dev"

# Optional: mark as dev if running in source directory
if os.path.exists(os.path.join(os.path.dirname(__file__), "..", "pyproject.toml")):
    # Indicates a local dev environment
    if not __version__.endswith("-dev"):
        __version__ += "-dev"

from .agents import Agent
__all__ = ["Agent"]