# CareerOS — Google Cloud Gmail Development Checklist

## Current implementation state

CareerOS keeps Google Sign-In and Gmail mailbox authorization separate. Google Sign-In uses only `openid profile email`. Gmail connection requests incremental readonly mailbox access using:

- `openid`
- `email`
- `profile`
- `https://www.googleapis.com/auth/gmail.readonly`

CareerOS deliberately does **not** request `https://mail.google.com/`, Gmail send, or Gmail modify for this milestone.

## GOOGLE CLOUD ACTION REQUIRED

1. Select the Google Cloud project that owns the `GOOGLE_CLIENT_ID` in the CareerOS backend environment.
2. Configure the OAuth consent screen / Google Auth platform.
3. During local development, keep the application in **Testing** unless production verification is intentionally being completed.
4. Add the developer/test Google account under **Test users**.
5. Enable the **Gmail API** for the same Google Cloud project.
6. In Data Access / OAuth scopes, add the exact Gmail readonly scope used by the application: `https://www.googleapis.com/auth/gmail.readonly`.
7. Ensure the OAuth client has the exact backend callback URI:
   `http://localhost:8000/api/v1/auth/oauth/google/callback`
8. If the Google Cloud client also uses JavaScript origins for another Google flow, keep:
   `http://localhost:3000`
   as an authorized JavaScript origin where required by that client configuration.
9. Ensure the backend `.env` uses the same client ID/secret as the Google Cloud OAuth client. Never commit the secret.
10. Ensure `FRONTEND_BASE_URL=http://localhost:3000` for the local stack.
11. Restart the backend/frontend after environment changes.
12. Sign in first using Google Sign-In.
13. Open Settings → Email & communication sources → Connect Gmail / Google Workspace.
14. If Google displays `Access blocked: CareerOS has not completed the Google verification process`, confirm the signed-in Google account is listed under OAuth **Test users**. This is a Google consent-screen policy state; it is not fixed by weakening CareerOS security.

## Production

If CareerOS is released to general users with sensitive/restricted Google scopes, complete the applicable Google verification requirements before public use. Do not attempt to bypass Google's verification process.

## Diagnostics

Settings exposes provider, mailbox identity, requested/granted scopes where available, token presence/expiry, sync state and the last error without rendering access or refresh tokens.
