# Quickstart

This quickstart will get you up and running with Agentify Toolkit.

In this quickstart you will:

1. Install the Agentify Toolkit
2. Add Model Provider API Keys
3. Create your Agent
4. Run, Serve and Deploy the Agent

For a full list of CLI commands refer to the [CLI Reference](docs/CLI_REFERENCE.md)

### 1. Install the Agentify-Toolkit

```bash
pip install agentify-toolkit
```

### 2. Add an Model Provider API KEY

Copy the example environment file:

```bash
cp .env.example .env
```

Open the `.env` and populate with your API keys:

```bash
# OpenAI
OPENAI_API_KEY=your-openai-key

# Anthropic
ANTHROPIC_API_KEY=your-anthropic-key

# DeepSeek
DEEPSEEK_API_KEY=your-deepseek-key

# Mistral AI
MISTRAL_API_KEY=your-mistral-key

# X AI
XAI_API_KEY=your-xai-key

# Google
GOOGLE_API_KEY=your-google-key

# AWS Bedrock
BEDROCK_API_KEY=your-bedrock-key
```

All providers will automatically pick up the keys from `.env`.

#### Getting API Keys

To use Agentify, you need an API key from your chosen AI provider (e.g., Anthropic, OpenAI/XAI, Google, Amazon Bedrock). Instructions can be found in the root of the repo \<MODEL PROVIDER\>.md

**General guidance:**

1. Visit your provider’s developer or API dashboard.
2. Sign in or create an account if you don’t have one.
3. Generate a new API key and copy it.

### 3. Create an Agent

#### Option A: via CLI

```bash
agentify agent new
```

> Note: `new` is used in preference to `create`. `create` remains an alias.

#### Interactive fields:

| Field         | Description                                                      |
| ------------- | ---------------------------------------------------------------- |
| `name`        | this is the agent name e.g. my_agent                             |
| `description` | A general description for the agent e.g. a security agent        |
| `version`     | Hit Enter for default 0.1.0                                      |
| `provider`    | The Model Provider this agent will use e.g. anthropic            |
| `model`       | The Model this agent will use e.g. claude-sonnet-4-5             |
| `api key`     | Hit Enter for default <PROVIDER_API_KEY>                         |
| `role `       | Enter the role of your agent e.g. You are an AWS Security expert |

#### Option B: Manually via `agent.yaml`

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
```

### 4. Run the Agent

```bash
agentify run agent.yaml
```

**You've just built your first AI Agent with Agentify!**

### TIPS:

**Running multiple agents**

If you have multiple agents, put them in a single folder and run:

```bash
agentify run <folder_name>
```

Agentify will provide an interactive menu to choose which agent to run.

**Overriding the model**

Experiment with a different model using:

```bash
agentify run agent.yaml --provider=openai --model=gpt-5-nano
```

Ensure you have registered the appropriate provider API key.

### 5. Serve the Agent via Web UI or API

```bash
agentify serve agent.yaml
```

- Open your browser at http://127.0.0.1:8001
- Chat with your agent using the HTMX-powered web interface

### 6. Deploy Agents with the Runtime

#### Start the Runtime Server

```bash
agentify runtime start
```

#### Deploy Agents

```bash

# Single Agent
agentify deploy agent.yaml

# Multiple agents from folder
agentify deploy examples/agents
```

#### List Deployed Agents

```
agentify runtime list
```

#### Invoke an Agent

```bash
# Interactive chat
agentify runtime invoke <agent_name>

# Single-shot prompt
agentify runtime invoke <agent_name> --prompt "Here is my prompt"
```

> You can also use the HTMX web interface at http://127.0.0.1:8001 to chat with all deployed agents.

## Feedback & Issues

If you encounter any problems with this Quickstart, please [open an issue](https://github.com/backplane-cloud/agentify-toolkit/issues).
