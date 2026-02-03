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

| Feature                          | Description                                                   | Branch                   | Status              |
| -------------------------------- | ------------------------------------------------------------- | ------------------------ | ------------------- |
| [Model Gateway](docs/GATEWAY.md) | Model Gateway e.g. host provider that acts as a model router. | `feature/model-gateway`  | Delivered (v0.16.0) |
| [Tools](TOOLS.md)                | Ability to add Tools to Agents                                | `feature/tools`          | Delivered (v0.14.0) |
| Internal Tools                   | Internal tools e.g. internal.py                               | `feature/internal-tools` | In Progress         |

## Proposed

| Feature                      | Description                                                                                 | Branch                       | Status      |
| ---------------------------- | ------------------------------------------------------------------------------------------- | ---------------------------- | ----------- |
| Agent & Tool Registry        | To store Agent and Tool YAMLs                                                               | `feature/registry`           | Not started |
| Token Usage                  | Record Token Usage of Agent / Model / Provider                                              | `feature/token-usage`        | Not started |
| Memory                       | Agent Memory                                                                                | `feature/memory`             | Not started |
| Streaming                    | Stream LLM Responses in chat mode                                                           | `feature/streaming`          | Not started |
| Agent-to-Agent Communication | Agents can talk to other Agents                                                             | `feature/agent-to-agent`     | Proposed    |
| Agent Reproduction           | Agents can dynamically create new agents to serve sub goals                                 | `feature/agent-reproduction` | Proposed    |
| Namespaces                   | e.g. `agentify init` within `solution/` and then `agentify deploy solution` under namespace | `feature/deploy-namespace`   | Proposed    |
