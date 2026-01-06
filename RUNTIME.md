## Agent Runtime

Running the agents via

```bash
agentify run agent.yaml
```

or

```bash
agentify run examples/agents
```

is fine for local testing and development.

But the real magic begins when you can host the agents in an Agent Runtime.

Commands below are ideation to hit the Agents Runtime API to host them separately.

However, we will need to secure the runtime with credentials to https://agents.backplane.dev.

The API key will be encrypted.

```bash
# Set the default server
agentify server set https://agents.backplane.dev

# Show default server
agentify server show
# Default server: https://agents.backplane.dev

# Show running agents
agentify show
# NAME                 STATUS     PROVIDER   MODEL
# claude               running    anthropic  claude-sonnet-4-5
# grok                 stopped    x          grok-4

# Upload a new agent
agentify upload examples/claude.yaml

# Run an agent remotely
agentify run examples/grok.yaml

# Delete an agent
agentify delete grok
```
