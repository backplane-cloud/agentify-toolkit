# How to Obtain an Mistral AI Developer API Key

Follow these steps to create an Mistral AI account and generate an API key for use with Mistral AI models.

## 1. Create an Mistral AI Account

1. Visit the Mistral AI platform: <https://console.mistral.ai/>
2. Click **Sign Up** (or **Log In** if you already have an account).
3. Complete email verification and login.

## 2. Create an API Key

1. In the sidebar, click **API Keys**
2. Click **Create new key**.
3. Name your key (e.g., `local-dev`, `agentify-cli`, `production`).
4. Copy the generated key and store it securely.

> You will not be able to view the key again after leaving the page.

## 3. Store the Key Securely

Store the key in an environment variable:

```bash
export MISTRAL_API_KEY="your_api_key_here"
```

or via agentify:

```bash
agentify provider add mistral
```

## 5. (Optional) Test the API

Example test using `curl`:

```bash
curl https://api.mistral.ai/v1/chat/completions \
  -H "Authorization: Bearer $MISTRAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistral-small-latest",
    "messages": [
      {
        "role": "user",
        "content": "Hello, can you introduce yourself?"
      }
    ]
  }'
```

A JSON response indicates successful access.
