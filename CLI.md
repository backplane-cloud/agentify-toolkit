# Agentify CLI Reference

| Command                                | Arguments / Options                          | Description                                                                                   |
| -------------------------------------- | -------------------------------------------- | --------------------------------------------------------------------------------------------- |
| **Local Commands**                     |                                              |                                                                                               |
| `agentify run <file.yaml>`             | `--model <model_id>` `--provider <provider>` | Run a single agent with optional override on provider/model                                   |
| `agentify run <path>`                  |                                              | Run a single agent YAML file, or a folder of YAMLs (presents interactive menu for selection). |
| `agentify list <folder>`               |                                              | List agents in a folder interactively and select one to run.                                  |
| `agentify server set <url>`            |                                              | Set the default runtime server URL.                                                           |
| `agentify server show`                 |                                              | Show the current runtime server URL.                                                          |
| **Runtime Server Commands**            |                                              |                                                                                               |
| `agentify runtime list`                | `--server <url>`                             | List all agents currently deployed on the runtime server.                                     |
| `agentify runtime show <agent_name>`   | `--server <url>`                             | Show details of a specific agent on the runtime server.                                       |
| `agentify runtime load <path>`         | `--server <url>`                             | Upload (deploy) an agent YAML file to the runtime server.                                     |
| `agentify runtime delete <agent_name>` | `--server <url>`                             | Delete an agent from the runtime server.                                                      |
| **Configuration Commands**             |                                              |                                                                                               |
| `agentify config show`                 |                                              | Display current Agentify configuration (e.g., runtime server).                                |
| `agentify config set <key> <value>`    |                                              | Set a configuration value (future extensibility, e.g., auth token).                           |
