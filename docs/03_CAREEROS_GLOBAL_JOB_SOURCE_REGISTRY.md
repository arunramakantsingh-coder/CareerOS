# CareerOS — Global Job Source Registry

## Source Families
- LinkedIn
- Naukri
- Indeed
- Glassdoor
- Foundit/Monster
- Dice
- ZipRecruiter
- Wellfound
- NaukriGulf
- Bayt
- GulfTalent
- FlexJobs
- SEEK Australia
- SEEK New Zealand
- Trade Me Jobs
- Jora
- Remote OK
- We Work Remotely
- Remotive
- staffing/recruitment portals
- company career portals
- government/public job portals
- recruiter sources
- authorized email feeds

## Source Registry
```text
source_id
name
type
region
country
connector_type
api_available
feed_available
email_available
company_portal
remote_focus
enabled
authorization_required
authorization_status
last_success
last_failure
rate_limit
notes
```

## Connector Principles
- Prefer official APIs/feeds where available.
- Respect provider terms and technical restrictions.
- Do not assume every portal is scrapeable.
- Preserve source provenance.
- Store source URLs and identifiers.
- Normalize into a Canonical Job.
- Deduplicate across sources.
- Fail one connector without breaking the entire discovery pipeline.

## Discovery Flow
```text
Source → Connector → Raw Job → Normalize → Company Resolution
→ Original JD Resolution → Deduplicate → Canonical Job
→ Job DNA → Matching
```
