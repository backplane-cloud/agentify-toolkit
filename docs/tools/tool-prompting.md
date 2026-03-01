# Feature/toolprompt

## [0.20.0] - 2026-02-25

- Problem: We want human-in-the-loop for tool invocations
- `agentify run agent.yaml --toolprompt` will force the agent to prompt before making any tool calls
- This is basic control for now, can be evolved to trust levels of agents and tools.
