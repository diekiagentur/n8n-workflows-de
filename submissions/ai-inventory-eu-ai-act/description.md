## Who is this for

Compliance officers, data protection officers and IT leads who must keep an inventory of the AI systems their company uses under the EU AI Act.

## What this workflow does

Departments submit an AI system through an n8n form. A Code node normalizes the entry and runs a keyword pre-check against the Annex III high risk areas. GPT-4.1-mini then proposes a risk class - prohibited practice, high risk under Annex III, transparency obligation under Art. 50, or minimal risk - with reasoning, a counter argument and the resulting obligations. A second Code node validates that proposal: unknown classes are rejected, the keyword check overrides a classification that is too mild, and external output always adds the Art. 50 duty. Entries land in Google Sheets as proposals pending human review; prohibited, high risk or unclear cases are emailed to management.

## How to set up

1. Create a Google Sheet named "AI inventory" with the columns used in the Google Sheets node.
2. Replace YOUR_SHEET_ID and the example addresses in the Send Email node.
3. Connect your OpenAI, Google Sheets and SMTP credentials, then share the form link internally.

## Requirements

An OpenAI API key, a Google account with Sheets access and an SMTP mailbox.

## How to customize

Extend the keyword list with the terms your industry uses, or swap the OpenAI node for a locally hosted model when submissions can contain personal data.
