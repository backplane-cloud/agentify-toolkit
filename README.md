# Agentify-Toolkit

[![PyPI](https://img.shields.io/pypi/v/agentify-toolkit)](https://pypi.org/project/agentify-toolkit/)
[![Python Version](https://img.shields.io/pypi/pyversions/agentify)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue)](LICENSE)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/backplane-cloud/agentify-toolkit/blob/main/examples/notebooks/Agentify_Developer_Quickstart.ipynb)

**Build and experiment with AI agents using simple declarative specs.**

![Agentify Toolkit Logo](https://raw.githubusercontent.com/backplane-cloud/agentify-toolkit/main/agentify-logo-lg.png)

![agent](https://raw.githubusercontent.com/backplane-cloud/agentify-toolkit/main/agent.png)

Agentify is a lightweight, declarative-first toolkit for prototyping AI agents. It lets you define agents as YAML specs and test them rapidly from the CLI or Python, without committing to a framework or model provider.

> Note: Agentify is not a workflow orchestrator or production framework. It’s simply for agent building, experimentation and prototyping.

## Quickstart

For a more detailed step-by-step [Quickstart](QUICKSTART.md).

### 1. Install the Agentify-Toolkit

```bash
pip install agentify-toolkit
```

### 2. Configure Provider API Keys

You can configure provider keys either via the CLI or manually through `.env`.

#### Option A - Using the CLI

```bash
agentify provider add <provider>
```

This updates (or creates) your `.env` file and stores the key for the selected provider.

To list all configured providers:

```bash
agentify provider list
```

To remove a provider key:

```bash
agentify provider remove <provider>
```

#### Option B - Using a `.env` File

```bash
cp .env.example .env
```

Populate `.env `with your provider keys:

```bash
OPENAI_API_KEY=<your-openai-key>
ANTHROPIC_API_KEY=<your-anthropic-key>
XAI_API_KEY=<your-xai-key>
GOOGLE_API_KEY=<your-google-key>
BEDROCK_API_KEY=<your-bedrock-key>
MISTRAL_API_KEY=<your-mistral-key>
DEEPSEEK_API_KEY=<your-deepseek-key>
OLLAMA_API_KEY=<your-deepseek-key>
```

Any configured provider will be automatically detected at runtime.

For instructions on how to obtain an Model API key:

| Provider   | Model               | Link                                                              |
| ---------- | ------------------- | ----------------------------------------------------------------- |
| OpenAI     | GPT-4               | [How to obtain an OpenAI API Key](docs/providers/OPENAI.md)       |
| Google     | Gemini              | [How to obtain an Google API Key](docs/providers/GOOGLE.md)       |
| Anthropic  | Claude              | [How to obtain an Anthropic API Key](docs/providers/ANTHROPIC.md) |
| XAI        | Grok                | [How to obtain an XAI API Key](docs/providers/XAI.md)             |
| Mistral AI | Mistral             | [How to obtain an Mistra AI API Key](docs/providers/MISTRAL.md)   |
| Deepseek   | deepseek-chat       | [How to obtain an Deepseek API Key](docs/providers/DEEPSEEK.md)   |
| Ollama     | evstral-small-2:24b | [How to obtain an Ollama Cloud API Key](docs/providers/OLLAMA.md) |

Verify:

```bash
agentify provider list
```

Example Output:

```bash
Configured Providers:
  ✓ openai     (sk-s****)
  ✓ anthropic  (sk-a****)
  ✓ deepseek   (sk-5****)
  ✓ mistral    (XOsY****)
  ✓ xai        (xai-****)
  ✓ google     (AIza****)
  ✓ bedrock    (ABSK****)
  ✓ ollama     (4163****)
```

### 3. Create an Agent

You can generate an agent spec via the CLI:

```bash
agentify agent create
```

Or define one manually by creating `agent.yaml`:

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

Run an agent directly from its YAML spec:

```bash
agentify run agent.yaml
```

You’ve just built and executed your first AI agent with Agentify.

#### Running Multiple Agents

You’ve just built and executed your first AI agent with Agentify.

```bash
agentify run examples/agents
```

Agentify will present an interactive selector so you can choose which agent to execute.

#### Overriding the Model at Runtime

Models and providers can be swapped without editing the YAML. For example:

```bash
agentify run agent.yaml --provider=openai --model=gpt-5-nano
```

Using overrides is useful for experimentation or benchmarking. Ensure the required API key is configured.

## Programmatic Usage

```python
from agentify import Agent

# Create Agent
agent = Agent(
    name="Grok",
    description="X's Grok Agent",
    provider="x",
    model_id="grok-4",
    role="You are an AI Security Architect specialising in X AI Grok models"
)

# Sent Prompt
response = agent.run("Which AI LLM is the best in 1 sentence?")
print(response)
```

### Quick CLI Reference

| Action                    | Command                               |
| ------------------------- | ------------------------------------- |
| Run from YAML             | `agentify run agent.yaml`             |
| Run folder of agents      | `agentify run examples/agents`        |
| List agents interactively | `agentify agent list [<folder_name>]` |
| Add a provider API key    | `agentify provider add <p>`           |
| List provider credentials | `agentify provider list`              |

## Supported Providers & Keys

| Provider   | Env Var                           |
| ---------- | --------------------------------- |
| OpenAI     | `export OPENAI_API_KEY=...`       |
| Anthropic  | `export ANTHROPIC_API_KEY=...`    |
| Gemini     | `export GEMINI_API_KEY=...`       |
| XAI (Grok) | `export XAI_API_KEY=...`          |
| Bedrock    | `export AWS_BEARER_TOKEN_BEDROCK` |

Windows:

```powershell
$env:OPENAI_API_KEY="..."
```

## Installation

Install from PyPI:

```bash
pip install agentify-toolkit
```

From source:

```bash
git clone https://github.com/backplane-cloud/agentify-toolkit.git
cd agentify-toolkit
pip install .
```

## License

Apache 2.0 - see LICENSE
