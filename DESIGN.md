# Agentify Design Principles

## 1. Declarative-first

- Agents are defined in **YAML configuration**, not code
- Enables versioning, reproducibility, and ease of review
- Python API is an escape hatch, not the default

## 2. Minimalism

- Keep the API surface small:
  - `run` → single-shot prompts
  - `chat` → interactive session
  - `list` → discover agents
- Avoid unnecessary abstractions: no chains, graphs, or hidden layers

## 3. Provider-agnostic

- Abstract LLM providers behind a uniform interface
- Switching providers should **not require rewriting the agent logic**

## 4. Predictability

- Every agent behaves consistently across runs
- Explicit roles, versioning, and parameter control
- YAML schema validation ensures correctness before execution

## 5. Developer-first

- CLI and notebooks are **first-class experiences**
- Clear error messages and verbose/debug modes
- Easy to integrate into scripts, CI/CD, or orchestration pipelines

## 6. Extensibility

- Optional memory modules
- Optional tool integrations
- Optional advanced parameters for experimentation
- Always additive: new features **do not break existing YAML agents**
