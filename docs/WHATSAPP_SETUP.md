# WhatsApp Business integration setup

This is an integration boundary, not a claim that WhatsApp is already connected to a live Meta app.

## Required server configuration

Set these environment variables in the backend runtime:

- `WHATSAPP_APP_SECRET`: Meta app secret used to validate the `X-Hub-Signature-256` HMAC SHA-256 signature against the exact raw request body.
- `WHATSAPP_VERIFY_TOKEN`: random verification token used only for Meta webhook subscription verification.

Never commit either value. If a required secret is absent, the webhook returns `503 NOT_CONFIGURED`; it does not accept unsigned events.

## Configure an organization

1. Create the agency organization in the admin console.
2. Create a `WhatsAppIntegration` for that organization with the Meta `phone_number_id`.
3. Keep `is_enabled=False` until the Meta webhook URL and subscribed fields are verified.
4. Configure the callback URL as `https://<your-host>/api/v1/whatsapp/webhook/`.
5. Complete Meta's GET verification handshake using the configured verify token.
6. Enable the integration only after a signed test event is received and the organization/contact/message records are checked.

## Consent and outbound workflow

- New inbound contacts begin with consent `UNKNOWN`. An inbound message is not treated as marketing opt-in.
- Record an explicit `opt_in` or `opt_out` action with its source through `POST /api/v1/whatsapp/contacts/<contact-id>/consent/`.
- Outbound messages require `OPTED_IN` consent and are queued for human approval.
- A manager approval changes status to `APPROVED`, not `SENT`. A provider-backed outbound worker, retry policy, approved-template verification and delivery reconciliation still need implementation before sending real messages.
- Store only the minimum contact and message data needed for the business purpose, and define retention/deletion and access policies before production use.

## Verification checklist

- Missing secret returns `503`.
- Invalid signature returns `403`.
- Valid signed inbound message creates one record; replaying the same provider message ID does not create a duplicate.
- Inbound activity never automatically sets opt-in consent.
- Outbound without consent is rejected.
- Cross-organization contact IDs are rejected.
- Approval requires an authorized role and re-checks consent.
- Provider delivery states are accepted only for known outbound message IDs and a configured integration.
