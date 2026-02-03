# Tool Schema

1. [Schema Overview](#1-schema-overview)
2. [Common Fields](#2-common-fields)
3. [Tool Types](#3-tool-types)
4. [Local Tool Schema](#4-local-tool-schema)
5. [Remote Tool Schema](#5-remote-tool-schema)
6. [Actions Schema (Remote Tools)](#6-actions-schema-remote-tools)
7. [Defaults and Validation](#7-defaults-and-validation)
8. [Versioning Guidelines](#8-versioning-guidelines)
9. [Design Constraints](#9-design-constraints)
10. [Next Steps](#10-next-steps)

This document is the authoritative reference for defining tools in Agentify.

It describes the full YAML schema used by both local and remote tools. This document is intentionally precise and implementation-focused.

For conceptual guidance, see Tools. For step-by-step tutorials, see Local Tools or Remote Tools.

## 1. Schema Overview

All tools are defined using a single YAML file.

At a minimum, a tool definition declares:

- Identity (name, version, description)

- Tool type (local or remote)

- The capability interface exposed to agents

```yaml
name: example_tool
type: local | remote
version: "1.0.0"
description: Short description of the tool
vendor: tool_author
```

## 2. Common Fields

These fields are supported by all tool types.

| Field         | Type   | Required | Description                                    |
| ------------- | ------ | :------: | ---------------------------------------------- |
| `name`        | string |   yes    | Unique tool identifier referenced by agents    |
| `type`        | string |    no    | `local` or `remote` (defaults to `remote`)     |
| `version`     | string |   yes    | Tool version (semantic versioning recommended) |
| `description` | string |   yes    | Human-readable description of the tool         |
| `vendor`      | string |    no    | Tool author or provider                        |

## 3. Tool Types

The type field determines how the tool is executed.

| Type     | Description                                            |
| -------- | ------------------------------------------------------ |
| `local`  | Executes a Python function inside the Agentify runtime |
| `remote` | Executes via HTTP outside the Agentify runtime         |

If omitted, the tool defaults to `remote`.

## 4. Local Tool Schema

Local tools bind declarative metadata to a Python function.
Required Fields

| Field      | Type   | Required | Description                           |
| ---------- | ------ | -------- | ------------------------------------- |
| `module`   | string | yes      | Python module path used for import    |
| `function` | string | yes      | Function name to invoke               |
| `params`   | object | no       | Parameter schema exposed to the agent |

### Example

```yaml
name: add_numbers
type: local
version: "1.0.0"
description: Add two numbers
vendor: built-in

module: tools.add_numbers
function: add_numbers

params:
  a:
    type: number
    required: true
  b:
    type: number
    required: true
```

## 5. Remote Tool Schema

Remote tools describe an HTTP-based interface composed of one or more actions.

### Required Fields

| Field    | Type   | Required | Description                 |
| -------- | ------ | -------- | --------------------------- |
| endpoint | string | yes      | Base URL for the remote API |
| actions  | object | yes      | Map of callable actions     |

### Example

```yaml
name: random_user
version: "1.0.0"
description: Generate random user data
vendor: RandomUser

endpoint: "https://randomuser.me/api/"

actions:
  get_user:
    method: GET
    path: /
    params:
      query:
      page: integer
      results: integer
```

## 6. Actions Schema (Remote Tools)

Actions represent callable operations exposed by a remote tool.

### Action Fields

| Field  | Type   | Required | Description                                |
| ------ | ------ | -------- | ------------------------------------------ |
| method | string | yes      | HTTP method (GET, POST, PUT, DELETE, etc.) |
| path   | string | yes      | Path relative to the base endpoint         |
| params | object | no       | Parameter definitions grouped by location  |

Actions are referenced internally by name during tool invocation.

### Parameters Schema

Parameters define the inputs that a tool or action accepts.

They serve two purposes:

- Guide the language model during tool selection
- Enable validation before execution

#### Parameter Locations (Remote Tools)

| Location | Description          |
| -------- | -------------------- |
| query    | URL query parameters |
| path     | URL path parameters  |
| body     | Request body fields  |
| headers  | HTTP headers         |

#### Parameter Definition

Each parameter supports the following fields:

| Field       | Type    | Required | Description                                        |
| ----------- | ------- | -------- | -------------------------------------------------- |
| type        | string  | yes      | Data type (string, number, boolean, object, array) |
| required    | boolean | no       | Whether the parameter is required                  |
| description | string  | no       | Human-readable description                         |

##### Example

```yaml
params:
  query:
    page:
      type: number
      required: false
      description: Page number to retrieve
```

## 7. Defaults and Validation

- Missing optional parameters are omitted from execution

- Required parameters are validated before invocation

- Invalid parameters result in tool invocation failure

Validation occurs before any local execution or remote request is made.

## 8. Versioning Guidelines

- Use semantic versioning (MAJOR.MINOR.PATCH)

- Increment MAJOR when breaking parameter or action changes occur

- Increment MINOR when adding backward-compatible capabilities

- Increment PATCH for fixes and documentation changes

Agents rely on tool stability for reliable execution.

## 9. Design Constraints

To ensure reliable agent behavior:

- Tool schemas should be explicit and minimal

- Avoid ambiguous parameter names

- Prefer multiple focused tools over a single broad one

- Do not expose internal-only or unstable endpoints

A well-defined schema improves both correctness and agent reasoning quality.

## 10. Next Steps

- See Tools for conceptual overview

- See Local Tools for Python-based implementation

- See Remote Tools for HTTP-based integrations

- See Agent Runtime for execution lifecycle details
