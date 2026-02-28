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
        __version__ = "0.0.0-dev"
except ImportError:
    __version__ = "0.0.0-dev"

if os.path.exists(os.path.join(os.path.dirname(__file__), "..", "pyproject.toml")):
    if not __version__.endswith("-dev"):
        __version__ += "-dev"

__all__ = []