# CareerOS — Matching & Skill Gap Intelligence

## 1. Purpose

The Matching Engine answers:

> How well does this opportunity fit the candidate and selected persona, why does it fit, what prevents success, and what should the candidate improve?

Keyword similarity alone is insufficient.

---

# 2. Inputs

```text
Career Passport
+
Career Vault Evidence
+
Persona
+
Job DNA
+
Opportunity Preferences
+
Remote / Mobility Constraints
```

---

# 3. Score dimensions

Initial configurable scoring:

| Dimension | Weight |
|---|---:|
| Technical / Capability | 25% |
| Relevant Experience | 20% |
| Architecture / Domain | 15% |
| Leadership / Seniority | 10% |
| Industry / Domain | 10% |
| Location / Remote | 5% |
| Salary | 5% |
| Migration / Relocation | 5% |
| Certification / Qualification | 5% |

The total equals 100%.

Weights must remain configurable.

---

# 4. Skill Match vs Overall Career Fit

These are separate.

### Overall Career Fit

Measures broader suitability.

### Skill Match

Measures direct/normalized capability alignment.

### Hard Eligibility

Measures constraints that can disqualify an opportunity.

A high Skill Match must never hide a hard failure.

---

# 5. Required 60% rule

```text
SKILL_MATCH >= 60%
        ↓
VISIBLE HIGH-POTENTIAL OPPORTUNITY
```

This means "worth explicit review."

It does **not** mean:

- automatically apply
- fully qualified
- no missing requirements
- legally eligible
- relocation-ready

---

# 6. Required job-card presentation

Example:

```text
DIGITAL RESILIENCE TRANSFORMATION LEAD

Career Fit            94%
Skill Match           64%   ★ 60% threshold crossed
Experience Fit        93%
Remote Fit             0%
Relocation Fit        95%
Visa Fit              82%
Salary Fit            88%

WHY THIS MATCHES
✓ Network transformation
✓ Cyber resilience
✓ Security architecture
✓ Governance
✓ Leadership

MATCHED
✓ Network Architecture
✓ Palo Alto
✓ Governance

PARTIAL
△ Cloud Security

TRANSFERABLE
⇄ Security transformation

MISSING
△ Australian regulatory experience
△ Local certification

HARD FAILURES
None

Recommended Persona
Security Architect

[Analyze JD] [View Skill Gaps] [Prepare Application]
```

---

# 7. Match categories

Every requirement should be one of:

- MATCHED
- PARTIAL
- MISSING
- TRANSFERABLE
- HARD_FAILURE
- NOT_APPLICABLE

The system must distinguish "missing exact technology" from "related transferable capability."

---

# 8. Hard failures

Examples:

- mandatory certification absent
- mandatory years of experience not met
- mandatory authorization unavailable
- explicit incompatible geography
- mandatory qualification absent
- other explicitly hard requirements

Hard failures must always be visible.

---

# 9. Skill Gap data model

## SkillGapObservation

Minimum fields:

```text
id
tenant_id
user_id
job_id
persona_id
skill_id / capability_id
status
requirement_type
confidence
evidence_id
source
observed_at
```

## SkillGapAggregate

Minimum fields:

```text
id
tenant_id
user_id
skill_id / capability_id
jobs_seen
jobs_missing
jobs_partial
mandatory_missing_count
personas_affected
role_families_affected
first_seen
last_seen
priority
learning_status
verified_at
```

The aggregate must be recalculable from observations.

---

# 10. Cumulative Skill Gap behavior

Every analyzed job contributes observations.

Examples:

```text
Kubernetes
18 jobs missing
13 mandatory
3 personas
5 role families
Priority HIGH

Terraform
14 jobs missing
6 mandatory
2 personas
Priority HIGH
```

The user should be able to move from:

```text
Job
→ Missing Skill
→ View cumulative occurrence
→ View affected personas
→ View affected opportunities
→ Mark learning
→ Add evidence after learning
→ Re-run matching
```

---

# 11. Gap priority

Priority should consider some combination of:

```text
frequency
× mandatory frequency
× opportunity volume
× persona impact
× market relevance
```

The exact formula should be configurable and documented.

---

# 12. Career improvement loop

```text
Job Analysis
 ↓
Skill Gap Observation
 ↓
Cumulative Gap DB
 ↓
Priority
 ↓
Learning / Experience
 ↓
Career Vault Update
 ↓
Evidence Added
 ↓
Future Jobs Re-matched
```

This turns CareerOS into a career development system, not a job rejection engine.

---

# 13. Required tests

- 59% threshold
- 60% threshold
- 61% threshold
- skill vs overall fit separation
- hard failure with high skill match
- direct match
- synonym
- transferable
- partial
- missing
- duplicate observations
- cumulative aggregation
- persona aggregation
- role-family aggregation
- tenant isolation
- explainability
- persistence
