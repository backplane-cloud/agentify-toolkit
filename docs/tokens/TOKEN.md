# Token Usage and Cost

## Features in v0.21.0

- Tokens are the unit of cost and the LLM providers have a rate for Input tokens and Output tokens.
- The ratio between input and output across providers is roughly 1:6, which means output tokens are on average 6x more expensive than input tokens
- Providers have several models which have different token rates
- Agentify provides visibility of token usage per LLM-call and per session.
- Agentify maintains an internal rate card so it can report the per-token cost of the call and session.

## Commands

| Command                                      | Behaviour                                      |
| -------------------------------------------- | ---------------------------------------------- |
| `agentify provider ratecard`                 | Displays the rate card for all provider models |
| `agentify provider ratecard <provider_name>` | Displays the rate card for a single provider   |

## [0.21.0] - 2026-02-28

### Feature/token-usage, token-cost (via ratecard)

- Token usage visibility per LLM call and response
- Token stats provider per LLM call, responding with input and output tokens for the turn call
- Agent has `input_tokens: int = 0` and `output_tokens: int = 0` these provide an accumulative count
- Implemented ratecard for each provide and model so the actual token usage cost can be returned to agent
