# How to Obtain an Anthropic Developer API Key

Follow these steps to create an Anthropic developer account and generate an API key for use with Claude models.

## 1. Create an Anthropic Account

1. Visit the Anthropic developer portal: <https://console.anthropic.com/>
2. Click **Sign Up** (or **Log In** if you already have an account).
3. Complete the email verification step (if prompted).

## 2. Accept Developer Terms

1. Once logged in, you may be asked to accept Anthropic’s **Developer Terms** and **Usage Policies**.
2. Confirm and proceed to the dashboard.

## 3. Set Up Billing (If Required)

1. In the sidebar, click **Billing**.
2. Add a payment method if required.
3. Review your available plan or credits.

> Note: New developers may receive free credits depending on region and availability.

## 4. Create an API Key

1. In the sidebar, click **API Keys**.
2. Click **Create Key**.
3. Name your key (e.g., `local-dev`, `agentify-runtime`, `production`).
4. Copy the generated key and store it securely.

> You will not be able to view the key again after leaving the page.

## 5. Store the Key Securely

Store the key in an environment variable:

```bash
# direct
export ANTHROPIC_API_KEY="your_api_key_here"
```

or via agentify:

```bash
# via agentify
agentify provider add anthropic
```

## 6. (Optional) Test the API

```bash
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-3-haiku-20240307",
    "max_tokens": 256,
    "messages": [{"role": "user", "content": "Hello Claude!"}]
  }'
```
