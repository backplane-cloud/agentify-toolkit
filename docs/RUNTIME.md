# Agent Runtime

The **Agent Runtime** allows you to **deploy your AI agents** to a dedicated host, interact with them via CLI or web UI, and manage their lifecycle.

| Command                  | Description                               |
| ------------------------ | ----------------------------------------- |
| `runtime start`          | Start the runtime server                  |
| `deploy <path>`          | Deploy a single or multiple agents        |
| `runtime list`           | List all loaded agents                    |
| `runtime invoke <agent>` | Invoke agent (interactive or single-shot) |

## 1. Start the Agent Runtime Server

```bash
# Start Agent Runtime server on http://127.0.0.1:8001
agentify runtime start
```

### 2. Deploy Agents

```bash
# Single Agent deployment
agentify deploy agent.yaml
```

```bash
# Multiple Agent Deployment
agentify deploy examples/agents
```

### 3. List Agents

```bash
agentify runtime list
```

### 4. Invoke an Agent

```bash
# For Interactive Chat
agentify runtime invoke <agent_name>

# For single-shot prompt
agentify runtime invoke <agent_name> --prompt "Here is my prompt"
```

### 5. Web UI

- navigate to http://127.0.0.1:8001
- View all loaded agents
- Chat with agents using the HTMX-powered interface

### 6. Terminate an Agent

```bash
agentify runtime terminate <agent_name>
```

## Programmatic API Example:

```python
import requests

def main():

    # Set the URL endpoint
    endpoint = "http://127.0.0.1:8001/agents/<agent_name>/prompt"

    # Create prompt in JSON
    prompt = {"question": "Which AI model are you in 5 words"}

    # Post request
    response = requests.post(endpoint, json=prompt)

    if response.status_code == 200:
        data = response.json()
        print("Response", data)
    else:
        print(f"Request failed with status {response.status_code}: {response.text}")

if __name__ == "__main__":
    main()
```

| Command                       | Description                 |
| ----------------------------- | --------------------------- |
| `/agents/add`                 | Create an Agent             |
| `/agents/<agent_name>/prompt` | Single Shot prompt to agent |
| `/`                           | List all loaded agents      |
