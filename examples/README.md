# Agentify Examples

These examplse demonstrate different ways to use Agentify:

- Declarative agents via YAML
- CLI-based excution
- Programmatic usage as a Python library

Each example is self-contained and can be run independently.

## Examples

### Declarative

#### Example 1: Declative - single-agent mode

```bash
agentify run agent.yaml
```

#### Example 2: Declative - multi-agent mode

```bash
agentify run examples/agents
```

### Programmatic

#### Example 1: Programmatic via `agent.run(<prompt>)`

```bash
python3 simple_agent.py
```

#### Example 2: Programmatic via `agent.chat()`

```bash
python3 chat_agent.py
```

### Example 3: Client Server

To run your Agent in server mode:

```bash
agentify run examples/agent.yaml --web
```

```bash
python3 client.py
```
