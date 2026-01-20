# How to Obtain an Ollama Cloud Developer API Key

Follow these steps to create an Ollama account and generate an API key for use with Ollama models.

## 1. Create an Ollama Account

1. Visit the Ollama platform: <https://ollama.com/>
2. Sign in and from the menu select Settings

## 2. Create an API Key

1. Click **Create API Key**
2. Name your key (e.g., `local-dev`, `agentify-cli`, `production`).
3. Copy the generated key and store it securely.

> You will not be able to view the key again after leaving the page.

## 3. Store the Key Securely

Store the key in an environment variable:

```bash
export OLLAMA_API_KEY="your_api_key_here"
```

or via agentify:

```bash
agentify provider add ollama
```

## 5. (Optional) Test the API

Example test using `curl` if API is exported:

```bash
curl https://ollama.com/api/chat \
  -H "Authorization: Bearer $OLLAMA_API_KEY" \
  -d '{
    "model": "gpt-oss:120b",
    "messages": [{
      "role": "user",
      "content": "Why is the sky blue?"
    }],
    "stream": false
  }'
```

A JSON response indicates successful access.
