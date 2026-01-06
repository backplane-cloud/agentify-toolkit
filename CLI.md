# CLI Reference

## Commands

1. [Run](#run)
2. [List](#list)
3. [Providers](#providers)
4. [server](#server)
5. [runtime](#runtime)
6. [config](#config)

## Run

| Command                    | Arguments / Options                          | Description                                                                                   |
| -------------------------- | -------------------------------------------- | --------------------------------------------------------------------------------------------- |
| **Local Commands**         |                                              |                                                                                               |
| `agentify run <file.yaml>` | `--model <model_id>` `--provider <provider>` | Run a single agent with optional override on provider/model                                   |
| `agentify run <file.yaml>` | `--web`                                      | Run Agent in Web UI                                                                           |
| `agentify run <path>`      |                                              | Run a single agent YAML file, or a folder of YAMLs (presents interactive menu for selection). |

## List

| Command                  | Arguments / Options | Description                                                  |
| ------------------------ | ------------------- | ------------------------------------------------------------ |
| `agentify list <folder>` |                     | List agents in a folder interactively and select one to run. |

## Providers

| Command                                 | Arguments / Options | Description                                 |
| --------------------------------------- | ------------------- | ------------------------------------------- |
| `agentify providers list`               | -                   | List of AI Providers and API Key status     |
| `agentify providers add <provider>`     | Enter API KEY       | Adds a provider to the CLI                  |
| `agentify provideres remove <provider>` | -                   | Remove a provider from local providers.yaml |

## Server

| Command                     | Arguments / Options | Description                          |
| --------------------------- | ------------------- | ------------------------------------ |
| `agentify server set <url>` |                     | Set the default runtime server URL.  |
| `agentify server show`      |                     | Show the current runtime server URL. |

## Runtime

| Command                                | Arguments / Options | Description                                               |
| -------------------------------------- | ------------------- | --------------------------------------------------------- |
| `agentify runtime list`                | `--server <url>`    | List all agents currently deployed on the runtime server. |
| `agentify runtime show <agent_name>`   | `--server <url>`    | Show details of a specific agent on the runtime server.   |
| `agentify runtime load <path>`         | `--server <url>`    | Upload (deploy) an agent YAML file to the runtime server. |
| `agentify runtime delete <agent_name>` | `--server <url>`    | Delete an agent from the runtime server.                  |

## Config

| Command                             | Arguments / Options | Description                                                         |
| ----------------------------------- | ------------------- | ------------------------------------------------------------------- |
| `agentify config show`              |                     | Display current Agentify configuration (e.g., runtime server).      |
| `agentify config set <key> <value>` |                     | Set a configuration value (future extensibility, e.g., auth token). |
