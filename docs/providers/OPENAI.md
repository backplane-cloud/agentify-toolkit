# How to Obtain an OpenAI Developer API Key

Follow these steps to create an OpenAI account and generate an API key for use with OpenAI models.

## 1. Create an OpenAI Account

1. Visit the OpenAI platform: <https://platform.openai.com/>
2. Click **Sign Up** (or **Log In** if you already have an account).
3. Complete email verification and login.

## 2. Set Up Billing

1. In the sidebar, click **Billing**.
2. Add a payment method if required.
3. Review your plan or free trial credits.

> Note: New accounts may receive free trial credits for testing.

## 3. Create an API Key

1. In the sidebar, under Manage, click **API Keys** or navigate to <https://platform.openai.com/account/api-keys>.
2. Click **Create new secret key**.
3. Name your key (e.g., `local-dev`, `agentify-cli`, `production`).
4. Copy the generated key and store it securely.

> You will not be able to view the key again after leaving the page.

## 4. Store the Key Securely

Store the key in an environment variable:

```bash
export OPENAI_API_KEY="your_api_key_here"
```

or via agentify:

```bash
agentify provider add openai
```

## 5. (Optional) Test the API

Example test using `curl`:

```bash
curl https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "Hello OpenAI!"}]
  }'
```

A JSON response indicates successful access.
