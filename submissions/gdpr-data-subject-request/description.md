## Who is this for

Data protection officers, legal and support teams who receive requests for access under Art. 15 GDPR and track them in a mailbox, where deadlines slip and nobody can prove who released which data.

## What this workflow does

A request is logged through an n8n form. A Code node calculates the deadlines as calendar months, not as 30 days, and writes the case into a Google Sheet that acts as the deadline register. Two branches run from there. The handling branch mails the data protection officer a case summary with two resume links and stops at a Wait node. Only after someone clicks "identity confirmed" does it query the internal data sources over HTTP, assemble a draft along the eight mandatory items of Art. 15 (1) and mail it back internally, never to the requester. The second branch waits until day 20 and reminds while the case is open.

## How to set up

1. Create a Google Sheet named "Data subject requests" with the columns used in the Google Sheets nodes.
2. Replace YOUR_SHEET_ID and the example addresses, and point "Query internal data sources" at your own endpoint.
3. Connect your Google Sheets and SMTP credentials.

## Requirements

A Google account with Sheets access and an SMTP mailbox. The lookup endpoint is optional.

## How to customize

Adjust the list of systems in the draft node, move the reminder off day 20, or replace the form trigger with an IMAP trigger on your privacy mailbox.
