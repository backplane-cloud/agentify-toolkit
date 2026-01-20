# How to Obtain a Google Gemini (Generative AI) API Key

Follow these steps to get an API key to access Google Gemini models via REST or SDK:

## 1. Create a Google Cloud Account

1. Visit the Google AI for Developers Console: <https://ai.google.dev/>
2. Click **Sign In** (or **Create Account** if you do not have one).
3. Complete any email verification or setup steps.
4. Go to <https://aistudio.google.com/>

## 2. Create an API Key

1. Click on Side Menu and Get API Key
2. Click **Create Credentials > API Key**.
3. Copy the generated key and store it securely.

> You can restrict the key by IP, HTTP referrers, or services for security.

## 5. Store the Key Securely

Store the key in an environment variable:

```bash
export GOOGLE_API_KEY="your_api_key_here"
```

or via agentify:

```bash
agentify provider add openai
```

## 6. (Optional) Test the API

Example test using `curl`:

```bash
curl -s -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent" \
  -H "x-goog-api-key: $GOOGLE_API_KEY" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{
    "contents": [
      {
        "parts": [
          {"text": "Hello! What is your model number."}
        ]
      }
    ],
    "generationConfig": {
      "temperature": 0.7,
      "maxOutputTokens": 150
    }
  }'
```

A JSON response indicates successful access.
