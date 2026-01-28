# How to Obtain a Github Models API Key

Agentify now supports Github Models. See [Changelog v0.15.0](../../CHANGELOG.md)

To get started, you will need a Github Personal Access Token.

## How to obtain a Github Personal Access Token

Steps:

- Login to Github
- Go to `Settings`
- Go to `Developer Settings`
- Click on `Personal access tokens`
- Select `Fine-grained tokens`
- Give your token a name e.g. agentify
- Add Permissions and type `models`.
- Click `Generate token`

Now with the token, add it to Agentify via the CLI:

```bash
agentify add provider github
```

Paste token when requested.

## Create Agent to test

Use CLI:

```bash
agentify agent create
```

| Field                                                         | Value                                                  |
| ------------------------------------------------------------- | ------------------------------------------------------ |
| Agent Name:                                                   | github                                                 |
| Description []:                                               | Github Models Agent                                    |
| Version [0.1.0]:                                              | _Press Enter to accept default_                        |
| Provider:                                                     | github                                                 |
| Model Id:                                                     | microsoft/Phi4                                         |
| API key environment variable name [GITHUB_API_KEY]:           | _Press Enter to accept default_                        |
| Define the agent's role. Enter multiple lines, then Ctrl+d... | My role is a Github Model Microsoft Phi 4 agent expert |

or create YAML:

```yaml
name: github
description: This is an example Github Models agent
version: 0.1.0
model:
  provider: github
  id: microsoft/Phi-4
  api_key_env: GITHUB_API_KEY
role: you are a github expert
```

Then run the agent:

```bash
agentify run github.yaml
```
