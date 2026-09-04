## Who is this for

Teams that run AI on their own hardware because the content is sensitive - HR files, patient records, design details - and need an endpoint applications can call without a prompt reaching a hosted provider.

## What this workflow does

A webhook accepts a JSON body with a question and an optional context. An IF node rejects oversized payloads with HTTP 400, then an HTTP Request node calls a locally hosted Ollama model. A Code node inspects the reply, because Ollama answers with HTTP 200 even when the model is not loaded or the context overflows - the body then carries an error string or an empty answer that would otherwise pass as a valid result. Successful calls are logged to Google Sheets as metadata only: timestamp, model, character counts and duration, never the prompt or the answer. If the model is unreachable or the reply unusable, the workflow answers HTTP 503 with the reason and four diagnostic steps. There is deliberately no silent failover to a cloud API - that would send exactly the data you self-host to keep private.

## How to set up

1. Install Ollama on the n8n host and pull a model.
2. Replace YOUR_OLLAMA_PORT, YOUR_MODEL_NAME and YOUR_SHEET_ID.
3. Give the webhook URL to the calling application.

## Requirements

An Ollama instance reachable from n8n and a Google account with Sheets access.

## How to customize

Change the default system prompt, raise the character limit for a model with a larger context window, or drop the Google Sheets node if you log elsewhere.
