# Backlog

### Status Key:

| Status      | Description                 |
| ----------- | --------------------------- |
| Proposed    | Proposed new feature        |
| Accepted    | Accepted for implementation |
| In Progress | Actively being implemented  |
| Delivered   | Feature implemented         |

# Features

## Delivered

### Features

| Feature                                     | Description                                                   | Branch                        | Status              |
| ------------------------------------------- | ------------------------------------------------------------- | ----------------------------- | ------------------- |
| [Provider Validation](docs/CLI.md)          | Provides validation of Provider API KEY                       | `feature/provider-validation` | Delivered (v0.18.0) |
| [Internal Tools](docs/tools/tools-local.md) | Internal tools e.g. internal.py                               | `feature/internal-tools`      | Delivered (v0.17.0) |
| [Model Gateway](docs/GATEWAY.md)            | Model Gateway e.g. host provider that acts as a model router. | `feature/model-gateway`       | Delivered (v0.16.0) |
| [Tools](TOOLS.md)                           | Ability to add Tools to Agents                                | `feature/tools`               | Delivered (v0.14.0) |

### Integrations

| Feature                                   | Description                         | Branch                     | Status |
| ----------------------------------------- | ----------------------------------- | -------------------------- | ------ |
| [Github Models](docs/providers/GITHUB.md) | Model Provider Github integrated    | `feature/github-models`    |        |
| [Deepseek](docs/providers/DEEPSEEK.md)    | Model Provider Deepseek integrated  |                            |        |
| [Mistral](docs/providers/MISTRAL.md)      | Model Provider Mistral integrated   | `feature/mistral-provider` |        |
| [Ollama](docs/providers/OLLAMA.md)        | Model Provider Ollama integrated    | `feature/ollama`           |        |
| [XAI](docs/providers/XAI.md)              | Model Provider XAI integrated       |                            |        |
| [Google](docs/providers/GOOGLE.md)        | Model Provider Google integrated    |                            |        |
| [OpenAI](docs/providers/OPENAI.md)        | Model Provider OpenAI integrated    |                            |        |
| [Anthropic](docs/providers/ANTHROPIC.md)  | Model Provider Anthropic integrated |                            |        |

## Proposed

| Feature                      | Description                                                                                 | Branch                       | Status      |
| ---------------------------- | ------------------------------------------------------------------------------------------- | ---------------------------- | ----------- |
| MCP Server                   | Agents can connect to MCP servers for tools e.g. `agentify mcp start`                       | `feature/mcp`                | In progress |
| Agent & Tool Registry        | To store Agent and Tool YAMLs                                                               | `feature/registry`           | Not started |
| Token Usage                  | Record Token Usage of Agent / Model / Provider                                              | `feature/token-usage`        | Not started |
| Memory                       | Agent Memory                                                                                | `feature/memory`             | Not started |
| Streaming                    | Stream LLM Responses in chat mode                                                           | `feature/streaming`          | Not started |
| Agent-to-Agent Communication | Agents can talk to other Agents                                                             | `feature/agent-to-agent`     | Proposed    |
| Agent Reproduction           | Agents can dynamically create new agents to serve sub goals                                 | `feature/agent-reproduction` | Proposed    |
| Namespaces                   | e.g. `agentify init` within `solution/` and then `agentify deploy solution` under namespace | `feature/deploy-namespace`   | Proposed    |
