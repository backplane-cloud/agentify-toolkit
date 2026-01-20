# How to Obtain an Deepseek Cloud Developer API Key

Follow these steps to create an Deepseek account and generate an API key for use with Deepseek models.

## 1. Create an Deepseek Account

1. Visit the Deepseek platform: <https://platform.deepseek.com>
2. Sign in and from the menu select Settings

## 2. Create an API Key

1. Click **API Key**
2. Create new API key
3. Name your key (e.g., `local-dev`, `agentify-cli`, `production`).
4. Copy the generated key and store it securely.

> You will not be able to view the key again after leaving the page.

## 3. Store the Key Securely

Store the key in an environment variable:

```bash
export DEEPSEEK_API_KEY="your_api_key_here"
```

or via agentify:

```bash
agentify provider add deepseek
```

## 5. (Optional) Test the API

Example test using `curl` if API is exported:

```bash
curl https://api.deepseek.com/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${DEEPSEEK_API_KEY}" \
  -d '{
        "model": "deepseek-chat",
        "messages": [
          {"role": "system", "content": "You are a helpful assistant."},
          {"role": "user", "content": "Hello!"}
        ],
        "stream": false
      }'
```

A JSON response indicates successful access.
