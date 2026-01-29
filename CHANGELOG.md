# Changelog

All notable changes to this project will be documented in this file.  
This project adheres to [Semantic Versioning](https://semver.org/).

---

## [0.16.0] - 2026-01-29

### New Feature / Model Gateway

- `agentify gateway start` starts Model Gateway provider called agentify
- Create agent with the provider set to `agentify`
- This will use the agentify provider which proxies the request ot the Model Gateway

---

## [0.15.0] - 2026-01-28

### New Feature / Github-Models

- Integrated Github Models
- Use github as a model (gateway) provider similar to Bedrock
- `agentify provider add github` refer to [documentation](docs/providers/GITHUB.md)

---

## [0.14.0] - 2026-01-21

### New Feature / Tools

- Agent now supports tools:

```bash
tools:
    - tool_1
    - tool_2
```

- The tools are loaded into the agent e.g. agent.tools.
- Performance: refactoring of cli.py to implement lazy loading to address CLI responsiveness

---

## [0.13.1] - 2026-01-20

### Added

- fixed missing Ollama Cloud: `agentify provider add ollama`

---

## [0.13.0] - 2026-01-20

### Added

- agentify provider add <provider_name>, remove, and list commands for managing API keys in .env
- Simplifies key management by storing keys directly in .env, no manual editing required
- Provides a beginner-friendly alternative to .env copy/edit workflows

---

## [0.12.0] - 2026-01-20

### Added support for Ollama Cloud and Ollama Local

- Install Ollama models locally and run Ollama server
- `agentify run examples/agents/ollama.yaml` and `ollama_local.yaml` examples

---

## [0.11.0] - 2026-01-18

### Added python-dotenv for better developer experience with environment variables

- Added `.env.examples`
- Providers retrieve API KEYS from dotenv as standard pattern

---

## [0.10.0] - 2026-01-18

### Integrated Mistral as a provider

- Added Mistral as a provider
- Example in examples/agents/mistral.yaml

---

## [0.9.0] - 2026-01-17

### Integrated Deepseek as a provider

- Added Deepseek as a provider
- Example in examples/agents/deepseek.yaml

---

## [0.8.0] - 2026-01-13

### Agentify Deploy and Runtime commands to host single and multi agents on a single endpoint

- Added `agentify runtime start` this creates an Agent Runtime on http://127.0.0.1:8001 for deploying agents to
- Added `agentify deploy agent.yaml` and `agentify deploy examples/agents` which loads a single agents or directory of agents
- Added `agentify runtime invoke agent_name --prompt "my prompt"` to speak to any agent
- Added `agentify runtime list` to view all running agents available on HTTP endpoint /agents/agent_name
- Added `agentify runtime terminate agent_name` to remove or unload the agent.

---

## [0.7.0] - 2026-01-12

### Added

- Added `agentify agents add` sub-command to interactively create an agent

---

## [0.6.0] - 2026-01-12

### Added

- Added `agentify agents list examples/agents` and `agentify agents show agent.yaml`

---

## [0.5.0] - 2026-01-12

### Added

- Added `agentify serve agent.yaml --port=8001` to replace `agentify run agent.yaml --web` keeps agentify run clean

---

## [0.4.3-alpha.1] - 2026-01-10

### Added

- Fixing Semantic Versions

---

## [0.4.2] - 2026-01-10

### Added

- Added --port to allow for custom port when serving agent with the --web switch

---

## [0.3.2] - 2026-01-10

### Added

- Added /prompt to Agent API Server to handle JSON request/response from clients

---

## [0.2.1] - 2026-01-08

### Added

- `--version` flag to the CLI

---

## [0.1.2] - 2026-01-08

### Fixed

- Forward reference in `Agent.chat` method for Python 3.10 compatibility
- Made `chat()` an instance method

---

## [0.1.0] - 2026-01-07

### Added

- Initial release with YAML-first agent definitions
- CLI for running and listing agents
- Programmatic `Agent` class for Python usage
- Support for multiple LLM providers: OpenAI, Anthropic, XAI, Gemini, Bedrock
- Interactive CLI and TUI for agent exploration
