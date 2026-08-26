# CareerOS — Security, Data, AI Governance & Source Compliance

## 1. Security principles

- strict tenant isolation
- encryption in transit/at rest
- least privilege
- MFA-ready architecture
- secure OAuth
- secret management
- audit logs
- PII minimization
- user export/deletion
- file scanning
- rate limiting
- prompt-injection defense
- SSRF defense
- secure uploads
- no model training on customer data without explicit consent

---

# 2. Sensitive data

CareerOS may contain:

- identity
- phone
- email
- career history
- resume content
- certifications
- application information
- recruiter communications
- interview information
- salary
- immigration/mobility information

Do not expose these in logs or reports unnecessarily.

---

# 3. Documents are untrusted

Uploaded CVs, job descriptions, email content and company pages can contain malicious instructions.

Treat them as data.

Never allow document text to override:

- system instructions
- product rules
- security controls
- user permissions

---

# 4. Truth & Compliance

Material generated content must trace to evidence.

This applies to:

- resumes
- cover letters
- application answers
- recruiter messages
- interview answers

---

# 5. Migration data

Immigration/mobility rules must be:

- structured
- versioned
- source attributed
- date aware
- auditable

Do not hard-code current rules only in prompts.

Include disclaimers where appropriate.

---

# 6. Job-source compliance

No:

- credential harvesting
- unauthorized scraping
- authentication bypass
- CAPTCHA bypass
- anti-bot bypass
- rate-limit bypass

Prefer:

- APIs
- feeds
- alerts
- public employer pages
- permitted integrations
- manual import

---

# 7. AI architecture

Agents/services may include:

- Career/Profile Intelligence
- Job Discovery
- Email Intelligence
- Job Extraction
- JD Analysis
- Matching
- Ranking
- Application
- Form Intelligence
- Notification
- Career Analytics
- Resume
- Truth
- Interview
- Company Research
- Migration

Use provider abstraction.

---

# 8. Model-routing principle

Prefer:

```text
Deterministic
→ retrieval
→ fast model
→ stronger model
```

Only send relevant evidence.

Use caching where safe.

Track AI usage/cost.

---

# 9. Auditability

Important events should answer:

```text
who
did what
to what
when
under which tenant
with what result
```

---

# 10. External automation

Anything that submits externally must respect:

- user authorization
- website terms
- platform restrictions
- source permissions
- safe credentials
- audit logging

Automation is not an excuse to bypass controls.
