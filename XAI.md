# How to Obtain an API Key for xAI (Grok)

Follow these steps to obtain an API key for the xAI Grok API:

---

## 1. Sign In or Create an Account with xAI

1. Go to the xAI developer portal: https://console.x.ai

---

## 2. Subscribe to an xAI Developer Plan

xAI offers several access tiers. The available plans typically include:

- **Free (limited)**
- **Pro**
- **Enterprise**

Choose the plan that suits your development needs.

---

## 3. Generate an API Key

1. Go to the Side Menu and click on API Keys
2. Click **Create API Key**.
3. Copy the generated key and store it securely.

---

## 5. Configure Access Scopes (Optional)

Depending on usage, xAI may allow you to scope access to:

- Chat completions
- Image or media generation (if supported)
- Rate limits

Adjust these if needed.

---

## 6. Test Your API Key (Example)

You can verify your key using `curl`:

```bash
  curl https://api.x.ai/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -d '{
    "model": "grok-2-latest",
    "messages": [
      {"role": "user", "content": "Hello from agentify-toolkit!"}
    ]
  }'
```
