# CareerOS — Authentication & Identity Specification
Status: AUTHORITY FOR IDENTITY DESIGN

## Purpose
Authentication is a product foundation, not an afterthought.

## Target Login / Registration
- Email + password
- Google OAuth/OIDC
- LinkedIn OAuth/OIDC
- Facebook OAuth/OIDC
- Additional OIDC providers later
- MFA capability

**Important source distinction:** the uploaded functional job-platform specification does not itself name Google/LinkedIn/Facebook login. The CareerOS Product Blueprint specifies Firebase Authentication or an equivalent managed identity service; Google/LinkedIn/Facebook are a requested product requirement from Arun and are therefore recorded here as the target provider set, subject to architecture/provider verification.

## CareerOS Authentication vs External Authorization
**Authentication:** who is the user?
**External authorization:** what external data did the user explicitly authorize?

Examples of external connections:
- Gmail/Google Workspace
- Microsoft mailbox
- job-alert feeds
- future connectors

These must be separate.

## Account Linking
If a person uses Google, LinkedIn, Facebook and email/password, validated linking should map them to one internal `user_id`, not silently create duplicate CareerOS accounts.

## Conceptual Data Model
```text
User
 ├── UserIdentity
 │     ├── provider
 │     ├── provider_subject
 │     └── verified_email
 ├── Session
 ├── MFA configuration
 ├── CareerVault
 ├── Personas
 ├── Jobs
 ├── Applications
 └── ExternalAccountConnection
```

## Security
- Secure password hashing
- Token/session expiry and refresh
- Logout
- Rate limiting
- MFA capability
- Audit logging
- Least privilege
- Encryption in transit/at rest
- Secrets management
- No OAuth tokens in logs
- Tenant isolation
- User-controlled export/deletion

## Acceptance Tests
AUTH-01 email registration
AUTH-02 email login
AUTH-03 logout
AUTH-04 invalid credentials rejected
AUTH-05 protected API rejects unauthenticated request
AUTH-06 Google login when configured
AUTH-07 LinkedIn login when configured
AUTH-08 Facebook login when configured
AUTH-09 safe provider linking
AUTH-10 session expiry/refresh
AUTH-11 secrets absent from logs
AUTH-12 external mailbox authorization is separate from login

## Provider Implementation Rule
Before implementing a provider, document protocol, redirect URI, scopes, callback route, token handling, environment variables, local configuration, production configuration and test method.

## UI Acceptance
Arun must be able to visibly test login, registration, logout and protected screens; provider login is tested when provider credentials/configuration are available.
