# CareerOS — Identity, Onboarding & Authentication

## Product target

The specification calls for:

- sign-up
- login
- password reset
- OAuth-ready architecture
- profile
- tenant isolation
- consent/security

The original project idea expands the desired user experience to:

- Google
- LinkedIn
- Apple
- Facebook
- Email + Password
- Phone OTP
- WhatsApp verification

---

# Authentication architecture

```text
Identity Provider
   ├── Google
   ├── LinkedIn
   ├── Apple
   └── Facebook
            +
Direct Identity
   └── Email / Password
            +
Phone Verification
   ├── SMS OTP
   └── WhatsApp OTP
            ↓
       Unified Identity
            ↓
          Tenant
            ↓
       Career Profile
```

Social providers are implementation integrations, not replacement product architecture.

---

# WhatsApp rule

WhatsApp must not be the sole authentication mechanism.

Use it as:

- verification channel
- notification channel
- optional OTP channel
- user communication channel

Possible notifications:

- job match alerts
- interview reminders
- application updates
- recruiter responses
- high-value opportunity alerts

---

# Tenant model

Every user belongs to a tenant context.

Tenant context must be derived from authenticated identity.

Never trust:

```text
tenant_id = request body
```

without authorization enforcement.

---

# Security tests

Required:

- registration
- duplicate registration
- login
- bad password
- token validation
- current user
- expired/invalid token
- protected route
- Tenant A / Tenant B isolation
- permission enforcement
- logout/session invalidation when implemented
- password reset
- verification flow

---

# Password and token rules

Use:

- secure password hashing
- signed access tokens
- externalized production secrets
- token expiry
- tenant-bound claims where appropriate

The repository's first authentication foundation uses bcrypt/passlib and python-jose; this is a foundation and still requires production hardening.

---

# Current known limitation

The reconciled status source records that the initial authentication foundation was implementation-in-progress and not yet fully runtime verified, and that domain routers still required comprehensive tenant-authorization retrofitting.

Therefore, never call identity/security "complete" based only on route existence.
