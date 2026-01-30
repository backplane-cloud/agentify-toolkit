# Backlog

## Features

| Features                         | Description                                                   | Status                           |
| -------------------------------- | ------------------------------------------------------------- | -------------------------------- |
| [Model Gateway](docs/GATEWAY.md) | Model Gateway e.g. host provider that acts as a model router. | Implemented (v0.16.0)            |
| [Tools](TOOLS.md)                | Ability to add Tools to Agents                                | Implemented (v0.14.0) 28.01.2026 |
| Tool/Agent Registry              | To store Agent and Tool YAMLs                                 | Not started                      |
| Token Cost                       | Record Token Usage of Agent / Model / Provider                | Not started                      |
| Memory                           | Agent Memory                                                  | Not started                      |

# Model Gateway

- Rather than specify a direct provider e.g. anthropic, the idea here is that you can specify a pseudo-provider e.g. `agentify` as the provider and then pass the vendor/model e.g. `anthropic/claude-sonnet-4-5`

- This will allow for scenarios of single-agent, multi-model.

# Agent/Tool Registry

The Agents and Tools are specified as YAML files.

The idea here is rather than `agentify run agent.yaml` we can do `agentify run namespace/agent_name`

Example:

```bash
agentify run backplane/cost_agent
```

and similar, the tools can be registered as `backplane/tool_a`. So at agent creation time, rather than check the local YAML file (default) it will retrieve from the registry server e.g. `http://localhost:8080/namespace/tools/<tool_name>/spec

# Tools

- Tools are a vital part of Agents. The LLM gives them inference/reasoning/planning. The Tools provide agency i.e. the ability to affect the world state, perform tasks etc.

- The philsophy here is declarative tools to describe API interfaces.

- Agents can have one or more tools.

  **Example tool**:

  ```yaml
  name: random_user
  version: "1.0.0"
  description: Generate random user data
  vendor: RandomUser
  endpoint: "https://randomuser.me/api/"
  actions:
    get_user:
      method: GET
      path: /
      params:
        query:
          page: integer
          limit: integer
  ```

  **Example Agent with tools**:

  ```yaml
  name: claude
  description: AI Engineer
  version: 0.1.0
  model:
    provider: anthropic
    id: claude-sonnet-4-5
    api_key_env: ANTHROPIC_API_KEY
  role: |
    You are an AI Security Engineer.
    Provide concise, practical answers with examples.
  tools:
    - random_user
  ```
