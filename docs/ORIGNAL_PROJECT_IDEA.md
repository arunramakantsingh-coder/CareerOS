Exactly — I would change the architecture based on what you just said. If the long-term goal is to make this public and monetize it, we should design it as a multi-tenant SaaS from day one, even if the first version is only for you.
And I agree with your biggest point:
The system must search by career capability, not job title.

That should actually become the core differentiator of the product.
1. Yes — make it SaaS
I would not build this as a private desktop tool.
Build:
AI Career & Global Job Intelligence SaaS

Initially:
You = first customer
Later:
Thousands of users = customers
Architecture:
                    ┌──────────────────────┐
                    │   WEB / MOBILE APP   │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │     API GATEWAY      │
                    └──────────┬───────────┘
                               │
             ┌─────────────────┼─────────────────┐
             ▼                 ▼                 ▼
       JOB ENGINE        CAREER ENGINE     MIGRATION ENGINE
             │                 │                 │
             └─────────────────┼─────────────────┘
                               ▼
                         AI ORCHESTRATOR
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
          JD ANALYZER     MATCH ENGINE     APPLICATION AI
Then every customer has:
Tenant
 │
 ├── Career Profile
 ├── Personas
 ├── Resume Versions
 ├── Preferences
 ├── Applications
 ├── Interviews
 └── Migration Profiles
2. Google Cloud is actually a very good fit
For your particular application, I would lean toward Google Cloud rather than WordPress or AWS for the initial SaaS.
A possible stack:
Frontend
   ↓
Firebase Hosting / App Hosting
   ↓
Cloud Run
   ↓
FastAPI / Python
   ↓
Cloud SQL PostgreSQL
   ↓
pgvector
   ↓
Cloud Storage
   ↓
AI APIs
Firebase has no-cost quotas for several services, including Hosting, Firestore and Storage. Cloud Run also has a monthly free tier, although you need billing enabled for Cloud Run. Google Help
So for an MVP / very small user base, your infrastructure bill can potentially be extremely low.
WordPress?
I'd use WordPress only for:
- marketing website
- blog
- SEO content
- landing pages
Not as the core application.
The actual application should be a proper SaaS platform.
3. And yes — SaaS from Day 1
Even if you have only yourself:
USER
 ↓
TENANT
 ↓
CAREER DATA
 ↓
AI
Later:
USER A ─┐
USER B ─┤
USER C ─┼── SaaS Platform
USER D ─┤
USER E ─┘
Data isolation must be designed from the beginning.
That's much easier than converting a single-user application into multi-tenant SaaS later.
4. Your second idea makes the product MUCH bigger
You mentioned:
Australia
New Zealand
migration abroad

I would actually make this a separate major module.
Not just:
Job Search
but:
Global Career + Migration Intelligence
The product could answer:
"Where can I realistically work and migrate based on my career?"

That's much more powerful.
5. Example of the future dashboard
Imagine a user enters their career profile.
The system produces:
GLOBAL CAREER MAP

🇮🇳 India
Job Match: 94%
Migration: N/A

🇦🇪 UAE
Job Match: 91%
Work Visa: HIGH
Relocation: HIGH

🇶🇦 Qatar
Job Match: 88%
Work Visa: HIGH

🇸🇦 Saudi Arabia
Job Match: 87%
Work Visa: HIGH

🇦🇺 Australia
Job Match: 84%
Skilled Migration: POSSIBLE
Employer Sponsorship: POSSIBLE

🇳🇿 New Zealand
Job Match: 86%
Skilled Residence: POSSIBLE

🇬🇧 UK
Job Match: 82%
Sponsorship: POSSIBLE

🇨🇦 Canada
Job Match: 79%
Immigration: CHECK

🇩🇪 Germany
Job Match: 81%
EU Blue Card: CHECK
That becomes a global career decision engine.
6. Australia module
The application should understand things such as:
Occupation
ANZSCO code
Skills assessment
Points
Age
Qualification
English
Work experience
State nomination
Employer sponsorship
Visa pathway
Australia has multiple skilled pathways, including employer-sponsored and points-tested routes, and its official occupation information uses ANZSCO classifications. Immigration and citizenship Website
For example, the system could say:
Your profile appears relevant to these Australian occupation classifications.

Then:
Occupation candidate
       ↓
ANZSCO
       ↓
Skills assessment authority
       ↓
Occupation eligibility
       ↓
Visa options
       ↓
State/territory options
       ↓
Relevant jobs
That's far more useful than simply searching:
"Network Architect Australia"

7. New Zealand module
Same concept.
The system should understand:
Occupation
NOL / ANZSCO where applicable
Green List
Skilled Migrant Category
Accredited Employer
AEWV
Salary threshold
Qualification
Experience
Residence pathway
New Zealand's official system currently includes the Skilled Migrant Category and Green List pathways, and the Skilled Migrant Category is tied to factors such as skilled employment, qualifications/registration/income and points. Immigration New Zealand
And importantly, New Zealand is changing its Skilled Migrant Category on 24 August 2026, so our migration engine must be designed around versioned rules, rather than hard-coding today's rules. Immigration New Zealand
That's an important architectural requirement.
8. Migration rules should be a separate AI/data engine
Don't put immigration rules inside prompts.
Instead:
Migration Rules Database
        │
        ├── Australia
        ├── New Zealand
        ├── Canada
        ├── UK
        ├── Germany
        ├── UAE
        ├── Qatar
        ├── Saudi Arabia
        └── Singapore
Every rule has:
Country
Visa
Requirement
Value
Effective Date
Expiry Date
Source
Last Verified
For example:
NZ SMC
Rule:
Age <= 55

Effective:
2026-08-24

Source:
Immigration New Zealand

Last Verified:
2026-08-11
That makes the system auditable.
9. Now your MOST important point: Job titles
You're absolutely right.
This would be a bad search engine:
Network Architect
Security Architect
Cyber Security Architect
Infrastructure Architect
Network Manager
IT Manager
because companies use completely different titles.
For example, a company could advertise:
Technology Solutions Lead

but the JD says:
Design enterprise network architecture
Lead Palo Alto firewall architecture
Develop Zero Trust architecture
Manage SD-WAN
Lead security transformation
That is potentially a very good match for you.
The title is irrelevant.
10. We need a "Career Capability Graph"
This is the key technology.
Instead of:
TITLE → JOB
we use:
JOB
 ↓
JOB DESCRIPTION
 ↓
CAPABILITIES
 ↓
SKILLS
 ↓
RESPONSIBILITIES
 ↓
ARCHITECTURE DOMAIN
 ↓
CAREER PROFILE
Example:
Job Title
Technology Transformation Lead
JD:
Lead enterprise network transformation, cybersecurity architecture, Zero Trust, cloud connectivity, firewall modernization and technology governance.

AI converts it into:
CAPABILITY VECTOR

Network Architecture       ██████████
Cyber Security             █████████
Security Architecture      █████████
Transformation             █████████
Governance                  ████████
Cloud                       ██████
Leadership                  ████████
Firewall                   █████████
Zero Trust                  ████████
Then compares against your career graph.
11. This is what I'd call the Job DNA Engine
Every job gets converted into a standardized internal representation.
JOB DNA
────────────────────────

Role Family:
Technology Architecture

Architecture:
Network
Security
Infrastructure

Security:
Palo Alto
Zero Trust
Firewall
Segmentation

Network:
Cisco
SD-WAN
Routing
Data Center

Leadership:
Team
Vendor
Program

Governance:
Risk
Compliance
Policy

Transformation:
Cloud
Modernization
Automation
Now the title doesn't matter.
12. We should also create a Role Ontology
This is a huge feature.
For example:
TECHNOLOGY
│
├── Infrastructure
│   ├── Network
│   │   ├── Architecture
│   │   ├── Operations
│   │   ├── SD-WAN
│   │   └── Data Center
│   │
│   ├── Cloud
│   └── Systems
│
├── Cyber Security
│   ├── Network Security
│   ├── Security Architecture
│   ├── SOC
│   ├── IAM
│   ├── NAC
│   ├── Zero Trust
│   └── GRC
│
├── Leadership
│   ├── IT Management
│   ├── Program Management
│   ├── Transformation
│   └── Vendor Management
│
└── Governance
    ├── Risk
    ├── Compliance
    ├── Policy
    └── Audit
Then the AI maps every JD into this ontology.
13. And this solves "weird job titles"
Consider:
Job A
Cloud Network Transformation Manager
Job B
Technology Risk Architect
Job C
Infrastructure Security Lead
Job D
Enterprise Technology Architect
Job E
Digital Resilience Architect
Job F
Cyber Transformation Lead
None of these necessarily contain:
Network Architect

But one or more could be highly relevant.
Your AI finds them.
14. Job discovery should have TWO engines
Engine A — Title Discovery
Traditional:
Network Architect
Security Architect
Cyber Security Architect
...
Engine B — Capability Discovery
AI searches based on:
Palo Alto
Cisco
Firewall
BGP
SD-WAN
Zero Trust
Network Security
Security Architecture
DORA
Cyber Resilience
Infrastructure
Governance
Architecture
Transformation
Leadership
Then:
Engine C — Semantic Discovery
This is the killer.
Search the meaning of the JD, not just keywords.
15. Example
Suppose job says:
Responsible for enterprise connectivity, secure network transformation, perimeter security, cloud connectivity, segmentation, and technology resilience.

No:
❌ Network Architect
No:
❌ Cyber Security Architect
But AI understands:
Enterprise Network
+
Network Security
+
Architecture
+
Cloud
+
Segmentation
+
Resilience
And returns it.
That's the product's differentiator.
16. Job sources
I'd build a Job Source Connector Framework.
Instead of hard-coding portals:
JobSource
    │
    ├── LinkedIn
    ├── Naukri
    ├── Naukri Gulf
    ├── foundit / Monster
    ├── Indeed
    ├── Bayt
    ├── FlexJobs
    ├── Glassdoor
    ├── Wellfound
    ├── Dice
    ├── ZipRecruiter
    ├── SEEK Australia
    ├── SEEK New Zealand
    ├── Jora
    ├── GulfTalent
    ├── Michael Page
    ├── Hays
    ├── Robert Half
    └── Company Career Pages
foundit is particularly relevant because it is now the successor to Monster in India and exposes jobs by skills, location, industry, functions and roles, which aligns well with the capability-based model we're proposing. Foundit
For international coverage I'd also add:
Middle East
- Bayt
- GulfTalent
- Naukrigulf
- LinkedIn
- Indeed
- company career sites
- recruitment firms
Australia
- SEEK
- Indeed
- LinkedIn
- Jora
- company career sites
New Zealand
- SEEK NZ
- Trade Me Jobs
- Indeed
- LinkedIn
- company career sites
Global Remote
- FlexJobs
- Remote OK
- We Work Remotely
- Wellfound
- Remotive
- Working Nomads
- Remote.com jobs
- company career pages
But there's an important implementation distinction:
We should not assume we can scrape every site.
The connector framework should support:
API
RSS/feed
Email alert
Public search
Partner feed
User-provided URL
Browser-assisted discovery
Company career page
and respect each site's terms.
17. Remote International deserves its own engine
Not:
Remote jobs

but:
Remote Eligibility Engine
Because:
Remote ≠ Remote from India.

A US company might say:
Remote
but actually mean:
Remote within United States.

Our system needs to classify:
REMOTE TYPE

🌍 Worldwide
🇮🇳 India only
🇺🇸 US only
🇪🇺 EU
🇬🇧 UK
🌏 APAC
🌎 Americas
🗺 Country restricted
❓ Unknown
Then:
User location
India
Job
Remote — US only
Result:
🔴 Not eligible
But:
Remote — Worldwide
🟢 Eligible
18. Even better: timezone compatibility
Suppose:
India
GMT +5:30

US East
GMT -5
The system could calculate:
Required overlap:
5 hours

Compatibility:
MEDIUM
Then:
Australia
HIGH
New Zealand
HIGH
Singapore
HIGH
Middle East
HIGH
Europe
HIGH
US
MEDIUM/LOW depending on schedule
This is incredibly useful for international remote workers.
19. Add relocation intent
Instead of simply searching:
Australia jobs

the user says:
I want to move to Australia.

Target:
Cyber Security / Network Security

Visa:
Employer sponsorship preferred

Location:
Sydney / Melbourne / Brisbane

Family:
Yes

Salary:
AUD X+

Relocation:
Required
Now the search engine optimizes for:
JOB MATCH
+
VISA POSSIBILITY
+
SPONSORSHIP
+
LOCATION
+
SALARY
+
RELOCATION
20. This creates an entirely new score
Instead of:
Job Match = 90%
We can show:
CAREER FIT              94%
VISA FIT                82%
LOCATION FIT            91%
SALARY FIT              88%
REMOTE FIT              100%
RELOCATION FIT          95%

────────────────────────────
GLOBAL OPPORTUNITY      91%
This is much more powerful.
21. The application could eventually tell you:
Don't apply to this job.

Even though the JD match is 94%.
Why?
Career Match: 94%
Visa Probability: 32%
Salary: Below target
Relocation: No sponsorship
Then:
🔴 SKIP
Conversely:
Career Match: 87%
Visa Probability: 96%
Salary: 95%
Relocation: 100%
🟢 APPLY
That's the intelligence people will actually pay for.
22. SaaS monetization
I'd eventually have:
FREE
1 Career Profile
2 Personas
20 Job analyses/month
Basic matching
PRO
₹499–999/month
- unlimited personas
- 500+ job analyses
- AI resume tailoring
- application tracking
- remote job intelligence
- recruiter messages
GLOBAL CAREER
₹1,499–2,499/month
Everything above +
- international jobs
- relocation intelligence
- Australia
- NZ
- UAE
- UK
- Canada
- Europe
- visa pathway matching
- salary intelligence
EXECUTIVE
₹3,000–5,000+/month
- executive roles
- CIO/CTO
- leadership positioning
- executive resume
- recruiter targeting
- interview intelligence
- career strategy
Pricing would need validation later, but the tier structure makes sense.
23. There is an even bigger business opportunity
Don't limit it to:
Job seekers.

Create:
Career Passport
A person creates one structured professional identity.
Career Passport
       │
       ├── Resume
       ├── LinkedIn
       ├── Job Profiles
       ├── Skills
       ├── Certifications
       ├── Projects
       ├── References
       ├── Achievements
       └── Career Evidence
Then:
"Find opportunities globally."

That's potentially much bigger than a resume builder.
24. And migration becomes a natural extension
Eventually:
CAREER PASSPORT
      │
      ├─────────────── JOBS
      │
      ├─────────────── REMOTE
      │
      ├─────────────── RELOCATION
      │
      ├─────────────── VISA
      │
      ├─────────────── SALARY
      │
      └─────────────── CAREER PLAN
The product becomes:
"Where should I work?"
not merely:
"Find me a job."
25. I would therefore change our original blueprint
The product should now have 7 major engines:
                    GLOBAL CAREER OS
                           │
       ┌───────────────────┼───────────────────┐
       │                   │                   │
       ▼                   ▼                   ▼
 CAREER ENGINE        JOB ENGINE         MIGRATION ENGINE
       │                   │                   │
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                           ▼
                    MATCH ENGINE
                           │
               ┌───────────┼───────────┐
               ▼           ▼           ▼
          APPLICATION   CAREER       INTERVIEW
             AI          AI             AI
                           │
                           ▼
                    ANALYTICS ENGINE
26. And the MOST important component
I would call it:
Career-to-Opportunity Intelligence Engine
Its job is:
Understand the person. Understand the job. Understand the market. Understand the country. Then determine whether this opportunity is worth pursuing.

That's fundamentally different from a job board.
Example
You:
18+ years IT / network / security / architecture / governance.

Job:
Digital Resilience Transformation Lead

Traditional search:
❌ Probably missed.
Our system:
JD
 ↓
Digital Transformation
Cyber Resilience
Network Security
Governance
Architecture
DORA
Risk
Leadership
 ↓
CAREER GRAPH
 ↓
Strong match
 ↓
Cyber Security Architect persona
 ↓
94% Career Fit
 ↓
Australia sponsorship available?
 ↓
YES
 ↓
Potential migration pathway
 ↓
🟢 HIGH-VALUE OPPORTUNITY
That is the product.
And because the rules, job markets, portals and visa requirements change, the SaaS architecture should be built around continuously updated data + source citations + versioned rules, not a static AI prompt.
For New Zealand especially, the official immigration site is already publishing 2026 rule changes, which demonstrates why this needs a live rules engine rather than hard-coded logic. Immigration New Zealand
My recommendation: Google Cloud + Cloud Run + PostgreSQL/pgvector + Firebase for the initial SaaS, with WordPress only if we want a separate SEO/marketing site. Google explicitly supports combining Firebase Hosting with Cloud Run for dynamic applications, and Cloud Run scales down when demand decreases, which is ideal for an early-stage SaaS. Google Cloud
The next step should therefore be to design the complete SaaS blueprint around these 7 engines, including the Career Ontology, JD/Job DNA model, Job Source Connector architecture, Australia/NZ migration engine, remote-work eligibility engine, multi-tenant database, subscription model, and the exact AI decision pipeline.

Google HelpImmigration and citizenship WebsiteImmigration New ZealandFounditGoogle Cloud