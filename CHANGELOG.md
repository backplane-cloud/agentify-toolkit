# Changelog

All notable changes to this project will be documented in this file.  
This project adheres to [Semantic Versioning](https://semver.org/).

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
