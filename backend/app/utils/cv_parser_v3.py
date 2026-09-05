from __future__ import annotations

import calendar
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.utils.document_intelligence_v2 import segment_sections


class CVParser:
    """Conservative section-aware CV parser.

    Employment records are created only when a date anchor and a plausible employer/title
    pair can be recovered. Competency strips and sidebar skill fragments are never promoted
    to employment merely because they sit near a date.
    """

    SKILLS = {
        "Networking": ["routing", "switching", "BGP", "OSPF", "MPLS", "SD-WAN", "VLAN", "VPN"],
        "Security": ["firewall", "IPS", "IDS", "zero trust", "segmentation", "SIEM", "EDR", "DLP"],
        "Cloud": ["AWS", "Azure", "GCP", "cloud", "hybrid cloud", "multi-cloud"],
        "Infrastructure": ["server", "storage", "virtualization", "VMware", "Hyper-V", "Kubernetes", "Docker"],
        "Cybersecurity": ["threat", "vulnerability", "incident response", "malware"],
        "Automation": ["automation", "scripting", "CI/CD", "DevOps", "Ansible", "Terraform"],
        "Programming": ["Python", "Java", "Go", "Rust", "C++", "JavaScript", "TypeScript"],
        "Database": ["PostgreSQL", "MySQL", "MongoDB", "Redis", "Kafka", "Elasticsearch"],
        "Monitoring": ["Prometheus", "Grafana", "Datadog", "New Relic"],
    }
    TITLE_TERMS = ("architect", "architecture", "engineer", "engineering", "manager", "management", "director", "lead", "leader", "consultant", "consulting", "analyst", "specialist", "executive", "administrator", "officer", "head of", "chief", "cio", "cto", "vp", "vice president", "principal", "program", "project manager", "solution", "security", "network")
    COMPANY_TERMS = ("ltd", "limited", "inc", "corp", "corporation", "llc", "pvt", "private", "company", "group", "bank", "technologies", "technology", "systems", "services", "consultancy", "consulting", "solutions", "industries", "international")
    MONTHS = r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
    DATE_TOKEN_RE = re.compile(rf"\b(?:{MONTHS})[\s,./-]+(?:19|20)\d{{2}}\b|\b(?:19|20)\d{{2}}[-/]\d{{1,2}}[-/]\d{{1,2}}\b|\b(?:19|20)\d{{2}}\b", re.I)
    DATE_RANGE_RE = re.compile(rf"(?P<start>(?:{MONTHS})[\s,./-]+(?:19|20)\d{{2}}|(?:19|20)\d{{2}}[-/]\d{{1,2}}[-/]\d{{1,2}}|(?:19|20)\d{{2}})\s*(?:[-–—]|to|until|through)\s*(?P<end>(?:{MONTHS})[\s,./-]+(?:19|20)\d{{2}}|(?:19|20)\d{{2}}[-/]\d{{1,2}}[-/]\d{{1,2}}|(?:19|20)\d{{2}}|present|current|now|till date|to date)\b", re.I)
    PRESENT_RE = re.compile(r"\b(present|current|now|till date|to date)\b", re.I)
    DEGREE_RE = re.compile(r"\b(Bachelor(?:'s)?|Master(?:'s)?|B\.?[A-Z]{1,4}\.?|M\.?[A-Z]{1,4}\.?|MBA|MSc|BSc|BEng|MEng|PhD|Doctorate|DBA|DPhil|Diploma)\b(?:\s+(?:of|in))?\s*([^,\n|]+)?", re.I)
    EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I)

    def parse(self, text: str, document_id: Optional[str] = None, document_category: Optional[str] = None) -> Dict[str, Any]:
        sections = segment_sections(text)
        category = (document_category or "cv").lower()
        personal = self._extract_personal(text, sections)
        professional = self._extract_professional(sections.get("experience", ""))
        skills = self._extract_skills(sections.get("skills", ""))
        certifications = self._extract_certification_document(text) if category == "certification" else self._extract_certifications(sections.get("certifications", ""))
        education = self._extract_education_document(text) if category == "education" else self._extract_education(sections.get("education", ""))
        if category == "employment" and not professional:
            professional = self._extract_employment_document(text)
        return {"personal": personal, "professional": professional, "skills": skills, "certifications": certifications, "education": education, "projects": self._extract_projects(sections.get("projects", "")), "achievements": self._extract_achievements(sections.get("achievements", "")), "sections": sections, "source_document_id": document_id, "confidence": self._calculate_confidence(personal, professional, skills, certifications, education), "extracted_at": datetime.utcnow().isoformat(), "version": "3.1-semantic-employment-boundaries"}

    def _extract_personal(self, text: str, sections: dict[str, str]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        lines = [x.strip() for x in text.splitlines() if x.strip()]
        for line in lines[:12]:
            if 2 <= len(line) <= 80 and not self.EMAIL_RE.search(line) and "linkedin" not in line.lower() and not re.search(r"\b(resume|curriculum vitae|profile|summary|cv)\b", line, re.I) and not self._contains_date(line):
                result["name"] = line
                break
        email = self.EMAIL_RE.search(text)
        if email:
            result["email"] = email.group(0)
        linkedin = re.search(r"(?:https?://)?(?:www\.)?linkedin\.com/in/[A-Za-z0-9_-]+", text, re.I)
        if linkedin:
            result["linkedin"] = linkedin.group(0)
        for line in lines[:30]:
            m = re.match(r"^(?:location|based in)\s*[:\-]\s*(.+)$", line, re.I)
            if m:
                result["location"] = m.group(1).strip()
            m = re.match(r"^(?:title|current role|position|designation)\s*[:\-]\s*(.+)$", line, re.I)
            if m:
                result["title"] = m.group(1).strip()
        if sections.get("summary"):
            result["summary"] = " ".join(x.strip() for x in sections["summary"].splitlines() if x.strip())[:4000]
        return result

    def _extract_professional(self, section: str) -> List[Dict[str, Any]]:
        if not section:
            return []
        lines = [self._normalize_layout_line(x) for x in section.replace("\r", "").splitlines() if x.strip()]
        if not lines:
            return []
        date_indices = [i for i, line in enumerate(lines) if self._contains_employment_date(line)]
        entries: List[Dict[str, Any]] = []
        used: set[tuple[str, str, str | None, str | None]] = set()

        for pos, idx in enumerate(date_indices):
            date_line = lines[idx]
            previous_boundary = date_indices[pos - 1] if pos else -1
            next_boundary = date_indices[pos + 1] if pos + 1 < len(date_indices) else len(lines)
            # A PDF/OCR extractor can place employer/title before or after the date. Search a
            # generous local window, but rank close, non-skill-strip lines above distant lines.
            candidate_rows: list[tuple[int, str]] = []
            for j in range(max(previous_boundary + 1, idx - 12), min(next_boundary, idx + 13)):
                if j == idx or self._contains_employment_date(lines[j]):
                    continue
                distance = abs(j - idx)
                value = self._strip_date_tokens(lines[j])
                if value and not self._looks_like_skill_strip(value):
                    candidate_rows.append((distance, value))

            company, title, confidence = self._infer_employer_and_title([value for _, value in sorted(candidate_rows, key=lambda x: (x[0], x[1]))])
            if not company or not title:
                c2, t2, conf2 = self._infer_employer_and_title([self._strip_date_tokens(date_line)])
                company = company or c2
                title = title or t2
                confidence = max(confidence, conf2)

            # Do not persist half-records. They are the source of the old "Employer not recorded"
            # and "B · CIO" artifacts. The user can still add a genuinely missing employment item.
            if not company or not title:
                continue

            item: Dict[str, Any] = {"company": company, "title": title, "location": self._extract_location(" ".join([x for _, x in candidate_rows] + [date_line])), "start_date": None, "end_date": None, "is_current": False, "responsibilities": [], "achievements": [], "confidence": confidence}
            self._apply_date_line(item, date_line)
            if not item.get("start_date"):
                continue

            # Content belongs to the role until the next date boundary. Header lines are filtered
            # out; actual responsibility/achievement bullets remain attached to this employment.
            for content_line in lines[idx + 1:next_boundary]:
                clean = self._clean_bullet(content_line)
                if not clean or self._looks_like_header_or_date(clean) or self._looks_like_skill_strip(clean):
                    continue
                if self._looks_like_achievement(clean):
                    item["achievements"].append(clean)
                elif len(clean) >= 24:
                    item["responsibilities"].append(clean)

            key = (self._norm(company), self._norm(title), item["start_date"], item["end_date"])
            if key not in used:
                used.add(key)
                entries.append(item)
        if not entries:
            entries.extend(self._extract_explicit_employment_labels(lines))
        return entries

    def _infer_employer_and_title(self, candidates: List[str]) -> tuple[str, str, float]:
        cleaned: list[str] = []
        seen: set[str] = set()
        for line in candidates:
            value = self._strip_date_tokens(line)
            value = re.sub(r"[•●▪◦]+", " ", value)
            value = re.sub(r"\s+", " ", value).strip(" -–—|·")
            if not value or len(value) > 220 or self._looks_like_skill_strip(value):
                continue
            key = self._norm(value)
            if key and key not in seen:
                seen.add(key)
                cleaned.append(value)

        # Strong explicit separators are safest: "Title | Company", "Company - Title", etc.
        for line in cleaned:
            parts = [p.strip() for p in re.split(r"\s*(?:\||@|\bat\b|[-–—]|·)\s*", line, maxsplit=1, flags=re.I) if p.strip()]
            if len(parts) != 2:
                continue
            left, right = parts
            lt, rt = self._title_likeness(left), self._title_likeness(right)
            lc, rc = self._company_likeness(left), self._company_likeness(right)
            if lt >= rt and (lt >= 0.55 or rc >= 0.35) and rc >= 0.35:
                return right, left, round(max(.76, lt, rc), 2)
            if rt > lt and (rt >= 0.55 or lc >= 0.35) and lc >= 0.35:
                return left, right, round(max(.76, rt, lc), 2)

        title_candidates = sorted(((self._title_likeness(v), v) for v in cleaned), reverse=True)
        company_candidates = sorted(((self._company_likeness(v), v) for v in cleaned), reverse=True)
        title_score, title_line = title_candidates[0] if title_candidates else (0.0, "")
        company_score, company_line = company_candidates[0] if company_candidates else (0.0, "")
        if title_line and company_line and title_line != company_line and title_score >= .55 and company_score >= .35:
            return company_line, title_line, round(max(.75, title_score, company_score), 2)
        return "", "", 0.0

    def _title_likeness(self, value: str) -> float:
        lower = value.lower()
        hits = sum(1 for term in self.TITLE_TERMS if re.search(rf"\b{re.escape(term)}\b", lower))
        if not hits:
            return 0.0
        return min(.94, .52 + .09 * hits)

    def _company_likeness(self, value: str) -> float:
        lower = value.lower()
        if self._looks_like_skill_strip(value):
            return 0.0
        hits = sum(1 for term in self.COMPANY_TERMS if re.search(rf"\b{re.escape(term)}\b", lower))
        score = min(.92, .42 + .10 * hits) if hits else 0.0
        # Acronyms such as CBI, IBM or HCL are common employer names.
        if re.fullmatch(r"[A-Z][A-Z0-9&.-]{1,15}", value.strip()):
            score = max(score, .72)
        # Proper-name company lines are plausible when they contain 1–6 words and no sentence
        # punctuation. Keep the score below a title match so titles still win ambiguous cases.
        words = value.split()
        if 1 <= len(words) <= 6 and re.fullmatch(r"[A-Za-z0-9&.'()/-]+(?:\s+[A-Za-z0-9&.'()/-]+){0,5}", value) and not re.search(r"[.!?:]$", value):
            if any(w[:1].isupper() for w in words):
                score = max(score, .38)
        return score

    def _looks_like_skill_strip(self, value: str) -> bool:
        value = re.sub(r"\s+", " ", value).strip()
        if value.count("|") >= 2:
            return True
        parts = [p.strip() for p in re.split(r"\||;|•|●|·", value) if p.strip()]
        if len(parts) >= 3 and all(len(p.split()) <= 9 for p in parts):
            return True
        # A long competency-only line is not a role header.
        if len(value.split()) >= 8 and not re.search(r"\b(company|corp|ltd|inc|university|college|director|manager|architect|engineer)\b", value, re.I):
            return True
        return False

    def _contains_employment_date(self, line: str) -> bool:
        if self.DATE_RANGE_RE.search(line):
            return True
        if self.PRESENT_RE.search(line) and self.DATE_TOKEN_RE.search(line):
            return True
        return len(self.DATE_TOKEN_RE.findall(line)) >= 2

    def _contains_date(self, line: str) -> bool:
        return bool(self.DATE_TOKEN_RE.search(line))

    def _apply_date_line(self, target: Dict[str, Any], line: str) -> None:
        m = self.DATE_RANGE_RE.search(line)
        if m:
            start = self._normalize_date(m.group("start"), False)
            end_token = m.group("end")
            end = None if self.PRESENT_RE.fullmatch(end_token.strip()) else self._normalize_date(end_token, True)
            target["start_date"], target["end_date"] = start, end
            target["is_current"] = end is None and bool(self.PRESENT_RE.search(end_token))
            return
        tokens = list(self.DATE_TOKEN_RE.finditer(line))
        if len(tokens) >= 2:
            values = [self._normalize_date(tokens[0].group(0), False), self._normalize_date(tokens[1].group(0), True)]
            if all(values) and values[0] > values[1]:
                values.reverse()
            target["start_date"], target["end_date"] = values[0], values[1]
            target["is_current"] = bool(self.PRESENT_RE.search(line)) and values[1] is None
            if self.PRESENT_RE.search(line):
                target["end_date"] = None
                target["is_current"] = True
            return
        if len(tokens) == 1 and self.PRESENT_RE.search(line):
            target["start_date"] = self._normalize_date(tokens[0].group(0), False)
            target["end_date"] = None
            target["is_current"] = True

    def _normalize_date(self, token: str, end: bool) -> str | None:
        token = token.strip()
        m = re.fullmatch(r"(19|20)(\d{2})[-/](\d{1,2})[-/](\d{1,2})", token)
        if m:
            return f"{m.group(1)}{m.group(2)}-{int(m.group(3)):02d}-{int(m.group(4)):02d}"
        y = re.fullmatch(r"(19|20)\d{2}", token)
        if y:
            return f"{token}-{'12-31' if end else '01-01'}"
        m = re.fullmatch(rf"({self.MONTHS})[\s,./-]+((?:19|20)\d{{2}})", token, re.I)
        if m:
            month = self._month_number(m.group(1))
            year = int(m.group(2))
            day = calendar.monthrange(year, month)[1] if end else 1
            return f"{year:04d}-{month:02d}-{day:02d}"
        return None

    def _month_number(self, value: str) -> int:
        return {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6, "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}.get(value.lower()[:3], 1)

    def _strip_date_tokens(self, value: str) -> str:
        value = self.DATE_RANGE_RE.sub(" ", value)
        value = self.DATE_TOKEN_RE.sub(" ", value)
        value = self.PRESENT_RE.sub(" ", value)
        return re.sub(r"\s+", " ", value).strip()

    def _normalize_layout_line(self, value: str) -> str:
        value = value.replace("\u00a0", " ").replace("\u2011", "-").replace("\ufeff", "")
        value = value.replace("\u2013", "-").replace("\u2014", "-")
        return re.sub(r"\s+", " ", value).strip()

    def _clean_bullet(self, value: str) -> str:
        return re.sub(r"^\s*[-•*✓▶●▪◦]+\s*", "", value).strip()

    def _looks_like_header_or_date(self, value: str) -> bool:
        if self._contains_employment_date(value):
            return True
        return bool(re.fullmatch(r"[A-Z][A-Z &/.-]{2,90}", value.strip())) and self._title_likeness(value) == 0

    def _extract_location(self, text: str) -> str | None:
        matches = re.findall(r"\(([^()]{2,80})\)", text)
        for match in matches:
            if not self._contains_date(match) and not self._looks_like_skill_strip(match):
                return match.strip()
        m = re.search(r"(?:location|based in|place of posting)\s*[:\-]\s*([^|]+)", text, re.I)
        return m.group(1).strip() if m else None

    def _extract_explicit_employment_labels(self, lines: List[str]) -> List[Dict[str, Any]]:
        company = title = None
        dates: Dict[str, Any] = {}
        for line in lines:
            m = re.match(r"(?:company|employer|organization)\s*[:\-]\s*(.+)", line, re.I)
            if m:
                company = m.group(1).strip()
            m = re.match(r"(?:designation|job title|position|role)\s*[:\-]\s*(.+)", line, re.I)
            if m:
                title = m.group(1).strip()
            if self._contains_employment_date(line):
                self._apply_date_line(dates, line)
        if company and title:
            return [{"company": company, "title": title, "location": None, "start_date": dates.get("start_date"), "end_date": dates.get("end_date"), "is_current": bool(dates.get("is_current")), "responsibilities": [], "achievements": [], "confidence": .72}]
        return []

    def _extract_employment_document(self, text: str) -> List[Dict[str, Any]]:
        company = self._label(text, ["company", "employer", "organization"])
        title = self._label(text, ["designation", "job title", "position", "role"])
        if not company or not title:
            return []
        item = {"company": company, "title": title, "location": self._extract_location(text), "start_date": None, "end_date": None, "is_current": False, "responsibilities": [], "achievements": [], "confidence": .65}
        for line in text.splitlines():
            if self._contains_employment_date(line):
                self._apply_date_line(item, line)
                break
        return [item]

    def _extract_skills(self, section: str) -> List[Dict[str, Any]]:
        if not section:
            return []
        result, seen = [], set()
        for raw in re.split(r"[,|;\n]", section):
            value = self._clean_bullet(raw)
            if not value or len(value) > 100 or len(value.split()) > 12:
                continue
            key = self._norm(value)
            if key in seen:
                continue
            seen.add(key)
            category = "Technical"
            for cat, words in self.SKILLS.items():
                if any(re.search(rf"\b{re.escape(word)}\b", value, re.I) for word in words):
                    category = cat
                    break
            result.append({"name": value, "category": category, "confidence": .82})
        return result

    def _extract_certifications(self, section: str) -> List[Dict[str, Any]]:
        if not section:
            return []
        result, seen = [], set()
        for raw in re.split(r"[,|\n]", section):
            line = self._clean_bullet(raw)
            if not line or len(line) > 180:
                continue
            explicit = bool(re.search(r"\b(certified|certification|credential|license|professional certificate)\b", line, re.I))
            known = bool(re.search(r"\b(CISSP|CISA|CISM|CRISC|CCSP|CCIE|CCNP|CCNA|PMP|ITIL|TOGAF|CEH|OSCP)\b", line, re.I))
            if not explicit and not known:
                continue
            key = self._norm(line)
            if key in seen:
                continue
            seen.add(key)
            result.append({"name": line, "issuer": self._label(line, ["issuer", "issued by", "from"]) or "Unknown", "issue_date": self._year(line), "confidence": .88})
        return result

    def _extract_certification_document(self, text: str) -> List[Dict[str, Any]]:
        name = self._label(text, ["certification", "certificate", "credential", "certification name"])
        if not name:
            for pattern in (r"(?:is hereby|has been awarded|successfully completed)\s+(?:the\s+)?(.{4,160}?(?:certification|certificate|credential))", r"(AWS Certified [^\n]+)", r"(Microsoft Certified [^\n]+)"):
                m = re.search(pattern, text, re.I)
                if m:
                    name = m.group(1).strip()
                    break
        if not name:
            return []
        return [{"name": name[:255], "issuer": (self._label(text, ["issuer", "issued by", "organization", "awarded by"]) or "Unknown")[:255], "credential_reference": self._label(text, ["credential id", "credential number", "certificate number", "license number"]), "issue_date": self._year(text), "expiry_date": self._expiry(text), "confidence": .93}]

    def _extract_education(self, section: str) -> List[Dict[str, Any]]:
        if not section:
            return []
        result = []
        for block in re.split(r"\n\s*\n", section):
            m = self.DEGREE_RE.search(block)
            if not m:
                continue
            degree = m.group(0).strip()
            field = (m.group(2) or "").strip() or None
            institution = None
            for line in block.splitlines():
                clean = line.strip()
                if re.search(r"\b(University|College|Institute|School|Academy)\b", clean, re.I):
                    institution = re.sub(r"\s*[,|].*$", "", clean).strip()
                    break
            if not institution:
                continue
            tmp: Dict[str, Any] = {}
            dm = self.DATE_RANGE_RE.search(block)
            if dm:
                self._apply_date_line(tmp, dm.group(0))
            result.append({"degree": degree[:255], "field": field, "institution": institution[:255], "start_date": tmp.get("start_date"), "end_date": tmp.get("end_date"), "confidence": .90})
        return result

    def _extract_education_document(self, text: str) -> List[Dict[str, Any]]:
        m = self.DEGREE_RE.search(text)
        if not m:
            return []
        institution = self._label(text, ["institution", "university", "college", "school", "institute"])
        if not institution:
            im = re.search(r"\b((?:University|College|Institute|School|Academy)\s+of\s+[A-Z][A-Za-z &.-]+|[A-Z][A-Za-z &.-]+\s+(?:University|College|Institute|School|Academy))", text)
            institution = im.group(1).strip() if im else None
        if not institution:
            return []
        return [{"degree": m.group(0).strip()[:255], "field": (m.group(2) or "").strip() or None, "institution": institution[:255], "start_date": None, "end_date": self._year(text), "confidence": .92}]

    def _extract_achievements(self, section: str) -> List[str]:
        return [self._clean_bullet(x) for x in section.splitlines() if x.strip() and self._looks_like_achievement(x)]

    def _extract_projects(self, section: str) -> List[Dict[str, Any]]:
        return [{"name": self._clean_bullet(x)} for x in section.splitlines() if x.strip()][:50]

    def _looks_like_achievement(self, text: str) -> bool:
        return bool(re.search(r"\b(increased|reduced|delivered|achieved|saved|grew|improved|led|launched|migrated|transformed|built|created|won)\b|\b\d+%\b|\$\s?\d", text, re.I))

    def _label(self, text: str, labels: list[str]) -> str | None:
        for label in labels:
            m = re.search(rf"{re.escape(label)}\s*[:\-]\s*([^\n]+)", text, re.I)
            if m:
                return m.group(1).strip()
        return None

    def _year(self, text: str) -> str | None:
        m = re.search(r"\b(19|20)\d{2}\b", text)
        return m.group(0) if m else None

    def _expiry(self, text: str) -> str | None:
        m = re.search(r"(?:expiry|expires|valid until)\s*[:\-]?\s*(\d{4})", text, re.I)
        return m.group(1) if m else None

    def _norm(self, value: str) -> str:
        return re.sub(r"[^a-z0-9]+", " ", (value or "").lower()).strip()

    def _calculate_confidence(self, personal, professional, skills, certifications, education) -> float:
        return round(min(.98, .45 + .11 * sum(bool(x) for x in (personal, professional, skills, certifications, education))), 2)
