# CareerOS — Email Connector Architecture

CareerOS treats mailbox access as a communication source, not an authentication dependency.

## Connector contract

All email providers target the same capability contract:

- connect / disconnect
- health_check
- sync
- fetch_messages
- fetch_thread
- search_messages
- get_metadata
- refresh_auth
- send_message (only where explicitly granted and human-approved)

## Providers

| Provider | Milestone state | Planned capability |
|---|---|---|
| Gmail / Google Workspace | Functional first provider | Read mailbox metadata/messages/threads/search |
| Outlook.com / Microsoft 365 | Architecture-ready, implementation next | Microsoft Graph delegated mail access |
| IMAP / SMTP | Planned fallback | Provider-specific OAuth/app-password handling where appropriate |
| Yahoo / iCloud / Fastmail / Zoho | Planned adapters | Provider-specific APIs or permitted IMAP/OAuth |

## Identity separation

A user can authenticate CareerOS with one identity provider and connect a different mailbox used for job hunting. The mailbox connector therefore stores its own provider, email address, capabilities, scopes and sync state.

## Opportunity pipeline

Email connector → validate → classify career intent → normalize sender/company/role/source → deduplicate → canonical opportunity/application event → Job DNA / Opportunity intelligence.

Supported future message intents include recruiter outreach, job alerts, application received, assessment, interview, rejection, offer, background verification, networking and unrelated mail.

## Security

Never request unrestricted mailbox access when a narrower scope works. Never log access/refresh tokens. External communication remains human-approved. Unsupported providers must be shown as unavailable/coming later rather than pretending connectivity exists.
