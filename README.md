# 📦 Agentify — Declarative AI Agent Toolkit

[![PyPI](https://img.shields.io/pypi/v/agentify)](https://pypi.org/project/agentify-toolkit/)
[![Python Version](https://img.shields.io/pypi/pyversions/agentify)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue)](LICENSE)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/backplane-cloud/agentify-toolkit/blob/main/examples/notebooks/Agentify_Developer_Quickstart.ipynb)

**Build and experiment with AI agents using simple declarative specs.**

Agentify is a lightweight, declarative-first toolkit for prototyping AI agents. It lets you define agents as YAML specs and test them rapidly from the CLI or Python, without committing to a framework or model provider.

> Use YAML for declarative specs, or Python for full control - both use the same agent model.

> Note: Agentify is not a workflow orchestrator, runtime platform, or production framework. It’s for rapid Agent building, experimentation and prototyping.

## Why Agentify ?

Most agent frameworks optimise for running agents - orchestration, routing, retries, supervision, cloud execution.

But before production comes a more important phase:
**figuring out what the agent should even do.**

Agentify optimises for that phase.

### Designed For:

✔ Rapid agent prototyping & ideation

✔ Teams exploring internal AI use cases

✔ Startups validating agent product ideas

✔ Teaching & education (low cognitive overhead)

✔ Provider portability (no early lock-in)

## Quickstart

### 1. Install

```bash
pip install agentify-toolkit
```

### 2. Add an LLM Provider Key

```bash
# anthropic | openai | xai | google | bedrock
agentify providers add <provider>
```

Verify:

```bash
agentify providers list
```

```bash
 anthropic
  env: ANTHROPIC_API_KEY
  status: READY
```

### 3. Create an Agent (YAML)

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

**You’ve just built your first AI agent with Agentify!**

> 💡 Tip: Running multiple agents

If you have multiple agents, put them in a single folder and run `agentify run <foldername>`. Agentify will provide an interactive menu so you can choose which agent you want to experiment with.

> 💡 Tip: Overriding the model

If you want to experiment with a different model, simply add `--provider=openai model=gpt-5-nano` to your call. Ensure you have registered the appropriate provider API key.

```bash
agentify run agent.yaml --provider=openai --model=gpt-5-nano
```

## Core Ideas

### 1. Declarative Agents (YAML-first)

Agents become artifacts:

- version controlled
- diffable
- shareable
- auditable

### 2. Provider Abstraction Without Lock-in

Most ecosystems ask:

> “Am I building on OpenAI, Anthropic, Bedrock, XAI, or Google?”

Agentify flips it:

> “The agent spec stays the same — only the provider changes.”

### 3. CLI-first Exploration

CLI interaction is fast, ergonomic, and repeatable:

```bash
agentify run agent.yaml
```

### 4. Agent = Single File

Agents collapse to a spec, not a codebase

### ✨ Key Features

📝 Declarative agent definitions via YAML

🔌 Multi-provider LLM support (OpenAI, Anthropic, XAI, Gemini, Bedrock)

💻 Interactive CLI and TUI for exploring agents

🐍 Programmatic API for custom workflows

🪶 Lightweight: Click + Rich + PyYAML

### 📚 Documentation & Notebooks

Prefer a guided walkthrough?

📘 Developer Quickstart (Notebook)
`examples/notebooks/Agentify_Developer_Quickstart.ipynb`

📄 YAML Deep Dive
`examples/notebooks/Agentify_YAML_Deep_Dive.ipynb`

## 🛠 Programmatic Usage

```python
from agentify import Agent

agent = Agent(
    name="Grok",
    description="X's Grok Agent",
    provider="x",
    model_id="grok-4",
    role="You are an AI Security Architect specialising in X AI Grok models"
)

response = agent.run("Which AI LLM is the best in 1 sentence?")
print(response)
```

### CLI Reference

| Action                    | Command                      |
| ------------------------- | ---------------------------- |
| Run from YAML             | `agentify run agent.yaml`    |
| Run folder of agents      | `agentify run agents/`       |
| List agents interactively | `agentify list agents`       |
| Add a provider API key    | `agentify providers add <p>` |
| List provider credentials | `agentify providers list`    |

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

📦 Installation (Detailed)
From PyPI:

```bash
pip install agentify-toolkit
```

From source:

```bash
git clone https://github.com/backplane-cloud/agentify-toolkit.git
cd agentify-toolkit
pip install .
```

## 📜 License

Apache 2.0 — see LICENSE
