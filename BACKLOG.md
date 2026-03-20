# Backlog

# Features

## Delivered

### Features

| Feature                                     | Description                                                                                     | Branch                        | Release |
| ------------------------------------------- | ----------------------------------------------------------------------------------------------- | ----------------------------- | ------- |
| Token Usage / Cost                          | Record Token Usage of Agent / Model / Provider with estimated cost                              | `feature/token-usage`         | v0.21.0 |
| [Tool Prompting](./CHANGELOG.md)            | Have agents prompt for approval before making tool call: `agentify run agent.yaml --toolprompt` | `feature/toolprompt`          | v0.20.0 |
| [MCP Server](docs/MCP.md)                   | Agents can connect to MCP servers for tools e.g. `agentify mcp start`                           | `feature/mcp`                 | v0.19.0 |
| [Provider Validation](docs/CLI.md)          | Provides validation of Provider API KEY                                                         | `feature/provider-validation` | v0.18.0 |
| [Internal Tools](docs/tools/tools-local.md) | Internal tools e.g. internal.py                                                                 | `feature/internal-tools`      | v0.17.0 |
| [Model Gateway](docs/GATEWAY.md)            | Model Gateway e.g. host provider that acts as a model router.                                   | `feature/model-gateway`       | v0.16.0 |
| [Tools](TOOLS.md)                           | Ability to add Tools to Agents                                                                  | `feature/tools`               | v0.14.0 |
| [Agent Runtime](docs/RUNTIME.md)            | Deploy multiple agents to Agent Runtime e.g. `agentify runtime start`                           |                               | v0.8.0  |
| Agent Serve                                 | Host a single Agent as an API HTTP Server                                                       |                               | v0.5.0  |

### Models Integrated

| Feature                                   | Description                         | Branch                     | Status  |
| ----------------------------------------- | ----------------------------------- | -------------------------- | ------- |
| [Github Models](docs/providers/GITHUB.md) | Model Provider Github integrated    | `feature/github-models`    | v0.15.0 |
| [Ollama](docs/providers/OLLAMA.md)        | Model Provider Ollama integrated    | `feature/ollama`           | v0.12.0 |
| [Mistral](docs/providers/MISTRAL.md)      | Model Provider Mistral integrated   | `feature/mistral-provider` | v0.10.0 |
| [Deepseek](docs/providers/DEEPSEEK.md)    | Model Provider Deepseek integrated  |                            | v0.9.0  |
| [XAI](docs/providers/XAI.md)              | Model Provider XAI integrated       |                            | v0.1.0  |
| [Google](docs/providers/GOOGLE.md)        | Model Provider Google integrated    |                            | v0.1.0  |
| [OpenAI](docs/providers/OPENAI.md)        | Model Provider OpenAI integrated    |                            | v0.1.0  |
| [Anthropic](docs/providers/ANTHROPIC.md)  | Model Provider Anthropic integrated |                            | v0.1.0  |

## Proposed

| Feature                      | Description                                                                                                              | Branch                       | Status      |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------ | ---------------------------- | ----------- |
| Memory                       | Agent Memory                                                                                                             | `feature/memory`             | Not started |
| Streaming                    | Stream LLM Responses in chat mode                                                                                        | `feature/streaming`          | Not started |
| Agent-to-Agent Communication | Agents can talk to other Agents                                                                                          | `feature/agent-to-agent`     | Proposed    |
| Agent Reproduction           | Agents can dynamically create new agents to serve sub goals                                                              | `feature/agent-reproduction` | Proposed    |
| Namespaces                   | e.g. `agentify init` within `solution/` and then `agentify deploy solution` under namespace                              | `feature/deploy-namespace`   | Proposed    |
| Model Classes                | Establish abstracted classes for model selection to use case e.g. flagship, mini, nano for example planner:worker:router | `feature/model-classes`      | Proposed    |
| Token Optmisation            | Stop sending tool schema per prompt and offload tool selection to budget-models to minimise token consumption and cost   | `feature/token-optimisation` | Proposed    |
| Agent Shell                  | Terminal User Interface based on Textual to provide Agent IDE                                                            | `feature/shell`              | Started     |
| Agent and Tool Registry      | The agent.yanml can be stored in a repository                                                                            | `feature/agent-registry`     | Proposed    |
