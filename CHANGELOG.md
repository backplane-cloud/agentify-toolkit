# Changelog

All notable changes to this project will be documented in this file.  
This project adheres to [Semantic Versioning](https://semver.org/).

---

## [0.3.1] - 2026-01-010

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
