# OpenAI
openai_rates = {
    "gpt-5.2": {"input_rate": 1.75, "output_rate": 14},
    "gpt-5.2-pro": {"input_rate": 21, "output_rate": 168},
    "gpt-5-mini": {"input_rate": 0.25, "output_rate": 2},
    "gpt-5-nano": {"input_rate": 0.05, "output_rate": 0.40},
    "gpt-4.1": {"input_rate": 2.0, "output_rate": 8.0},
    "gpt-4.1-mini": {"input_rate": 0.40, "output_rate": 1.60},
    "gpt-4.1-nano": {"input_rate": 0.10, "output_rate": 0.40}
}

# Anthropic
anthropic_rates = {
    "claude-opus-4.5": {"input_rate": 5, "output_rate": 25},
    "claude-sonnet-4-5": {"input_rate": 3, "output_rate": 15},
    "claude-haiku-4.5": {"input_rate": 1, "output_rate": 5},
}

# Google
google_rates = {
    "gemini-3-pro":         {"input_rate": 2.00, "output_rate": 12.00},
    "gemini-3-flash":       {"input_rate": 0.50, "output_rate": 3.00},
    "gemini-2.5-pro":       {"input_rate": 1.25, "output_rate": 10.00},
    "gemini-2.5-flash":     {"input_rate": 0.30, "output_rate": 2.50},
    "gemini-2.5-flash-lite":{"input_rate": 0.10, "output_rate": 0.40},
}

# Mistral
mistral_rates = {
    "mistral-small-latest": {"input_rate": 0.10, "output_rate": 0.30}
}

# X AI
x_rates = {
    "grok-4": {"input_rate": 3.00, "output_rate": 15.00},
    "grok-3": {"input_rate": 3.00, "output_rate": 15.00},
    "grok-3-mini": {"input_rate": 0.30, "output_rate": 0.50},
    "grok-4-fast-non-reasoning": {"input_rate": 0.20, "output_rate": 0.50},
    "grok-4-fast-reasoning": {"input_rate": 0.20, "output_rate": 0.50}
}

RATE_CARD = openai_rates | anthropic_rates | google_rates | mistral_rates | x_rates

def estimate_cost(model_id, input_tokens, output_tokens):
    # Default rates if model_id not found
    default_rates = {"input_rate": 0.0, "output_rate": 0.0}
    rates = RATE_CARD.get(model_id, default_rates)

    cost = (rates["input_rate"]/1_000_000) * input_tokens + (rates["output_rate"]/1_000_000) * output_tokens

    return cost