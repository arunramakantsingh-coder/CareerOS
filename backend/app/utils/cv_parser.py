import re
from datetime import datetime
from typing import Any, Dict, List, Optional


class CVParser:
    """Conservative, section-aware CV parser.

    Profile enrichment is intentionally CV-only. This parser also avoids the
    previous behaviour where generic words such as ``qualifications`` could
    pull unrelated text into certifications. A field is extracted only when
    it is found in the appropriate CV section or by a strong labelled pattern.
    """

    SECTION_ALIASES = {
        "summary": {"summary", "professional summary", "profile summary", "about me", "career summary"},
        "experience": {"experience", "work experience", "professional experience", "employment history", "work history", "employment"},
        "education": {"education", "academic background", "academic qualifications", "education & training"},
        "certifications": {"certifications", "certification", "professional certifications", "licenses & certifications", "credentials"},
        "skills": {"skills", "technical skills", "core skills", "key skills", "technologies", "technical competencies", "competencies"},
        "projects": {"projects", "key projects", "professional projects"},
        "achievements": {"achievements", "accomplishments", "awards", "recognition"},
    }

    def __init__(self):
        self.skill_categories = {
            "Networking": ["routing", "switching", "bgp", "ospf", "mpls", "sd-wan", "vlan", "vpn", "networking"],
            "Security": ["firewall", "ips", "ids", "zero trust", "segmentation", "siem", "edr", "dlp"],
            "Cloud": ["aws", "azure", "gcp", "cloud", "hybrid cloud", "multi-cloud"],
            "Infrastructure": ["server", "storage", "virtualization", "vmware", "hyper-v", "kubernetes", "docker"],
            "Cybersecurity": ["threat", "vulnerability", "incident response", "malware", "cybersecurity"],
            "Automation": ["automation", "scripting", "ci/cd", "devops", "ansible", "terraform"],
            "Programming": ["python", "java", "go", "rust", "c++", "javascript", "typescript"],
            "Database": ["postgresql", "mysql", "mongodb", "redis", "kafka", "elasticsearch"],
            "Monitoring": ["prometheus", "grafana", "datadog", "new relic"],
        }
        self.known_certifications = [
            "CISSP", "CISA", "CISM", "CRISC", "CCSP", "CCIE", "CCNP", "CCNA",
            "AWS Certified", "Azure", "PMP", "ITIL", "TOGAF", "CEH", "OSCP", "OSCE",
            "GIAC", "CompTIA Security+", "CompTIA Network+",
        ]

    @staticmethod
    def _clean_heading(line: str) -> str:
        return re.sub(r"[^a-z0-9&+/# -]", "", line.strip().lower()).strip(" -:|")

    def _sections(self, text: str) -> Dict[str, str]:
        """Split a CV into semantic sections using heading lines."""
        lines = text.replace("\r", "").split("\n")
        positions: List[tuple[int, str]] = []
        alias_to_section = {alias: section for section, aliases in self.SECTION_ALIASES.items() for alias in aliases}
        for index, line in enumerate(lines):
            cleaned = self._clean_heading(line)
            if cleaned in alias_to_section:
                positions.append((index, alias_to_section[cleaned]))
        sections: Dict[str, str] = {}
        for pos, (start, section) in enumerate(positions):
            end = positions[pos + 1][0] if pos + 1 < len(positions) else len(lines)
            block = "\n".join(lines[start + 1:end]).strip()
            # First occurrence wins; duplicate CV headings are normally layout noise.
            sections.setdefault(section, block)
        return sections

    def parse(self, text: str, document_id: Optional[str] = None) -> Dict[str, Any]:
        sections = self._sections(text)
        result = {
            "personal": self._extract_personal(text, sections),
            "professional": self._extract_professional(sections.get("experience", "")),
            "skills": self._extract_skills(sections.get("skills", "")),
            "certifications": self._extract_certifications(sections.get("certifications", "")),
            "education": self._extract_education(sections.get("education", "")),
            "projects": self._extract_projects(sections.get("projects", "")),
            "achievements": self._extract_achievements(sections.get("achievements", "")),
            "raw_text": text[:10000],
            "source_sections": sorted(sections.keys()),
            "confidence": self._calculate_confidence(sections),
            "extracted_at": datetime.now().isoformat(),
            "version": "2.0-section-aware",
        }
        return result

    def _extract_personal(self, text: str, sections: Dict[str, str]) -> Dict[str, Any]:
        personal: Dict[str, Any] = {}
        lines = [x.strip() for x in text.replace("\r", "").split("\n") if x.strip()]
        email = re.search(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", text, re.I)
        phone = re.search(r"(?:\+\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?)?\d{3,4}[\s.-]\d{3,4}", text)
        linkedin = re.search(r"(?:https?://)?(?:www\.)?linkedin\.com/in/[\w-]+", text, re.I)
        if email:
            personal["email"] = email.group(0)
        if phone:
            personal["phone"] = phone.group(0)
        if linkedin:
            personal["linkedin"] = linkedin.group(0)

        labelled = {
            "name": r"(?:full\s+name|candidate\s+name|name)\s*[:\-]\s*([^\n]+)",
            "location": r"(?:location|based\s+in|city)\s*[:\-]\s*([^\n]+)",
            "title": r"(?:professional\s+title|current\s+title|job\s+title|position)\s*[:\-]\s*([^\n]+)",
        }
        for key, pattern in labelled.items():
            match = re.search(pattern, text, re.I)
            if match:
                personal[key] = match.group(1).strip()

        if "name" not in personal:
            for line in lines[:8]:
                if len(line) <= 70 and not re.search(r"@|linkedin|phone|resume|curriculum vitae|^(summary|profile|experience|education|skills)$", line, re.I):
                    words = line.split()
                    if 2 <= len(words) <= 6 and all(re.match(r"^[A-Za-z.'-]+$", w) for w in words):
                        personal["name"] = line
                        break

        if "title" not in personal:
            summary = sections.get("summary", "")
            first = next((x.strip() for x in summary.splitlines() if x.strip()), "")
            if first and len(first) < 140:
                title_hint = re.search(r"\b(?:CISO|CTO|CIO|Director|Head|Manager|Architect|Engineer|Consultant|Analyst|Specialist|Developer|Lead|Principal)\b[^\n,|]{0,80}", first, re.I)
                if title_hint:
                    personal["title"] = title_hint.group(0).strip()
        if "summary" in sections:
            personal["summary"] = self._compact_block(sections["summary"], 1200)
        return personal

    @staticmethod
    def _compact_block(value: str, limit: int = 1200) -> str:
        return re.sub(r"\n{3,}", "\n\n", value.strip())[:limit]

    def _extract_professional(self, text: str) -> List[Dict[str, Any]]:
        if not text.strip():
            return []
        lines = [x.strip() for x in text.splitlines()]
        entries: List[Dict[str, Any]] = []
        current: Optional[Dict[str, Any]] = None
        date_re = re.compile(r"(?P<start>(?:\w+\s+)?\d{4}|\d{4})\s*(?:-|–|—|to)\s*(?P<end>(?:\w+\s+)?\d{4}|present|current)", re.I)
        title_re = re.compile(r"\b(?:chief|vice president|vp|director|head|senior|lead|principal|staff|manager|architect|engineer|consultant|analyst|specialist|developer|administrator|executive|officer)\b", re.I)
        for line in lines:
            if not line:
                continue
            date_match = date_re.search(line)
            if date_match and current:
                current["start_date"] = date_match.group("start")
                current["end_date"] = None if date_match.group("end").lower() in {"present", "current"} else date_match.group("end")
                current["is_current"] = current["end_date"] is None
                continue
            bullet = re.sub(r"^[•●▪◦*-]\s*", "", line)
            if current and line != bullet:
                if re.match(r"^[•●▪◦*-]\s+", line):
                    target = "achievements" if re.search(r"\b(achieved|delivered|increased|reduced|saved|won|led)\b", bullet, re.I) else "responsibilities"
                    current[target].append(bullet)
                    continue
            # New role heuristic: a short line containing a job-title word.
            if len(line) <= 140 and title_re.search(line) and not date_match:
                if current and (current.get("company") or current.get("title")):
                    entries.append(current)
                parts = re.split(r"\s+[|@]\s+|\s+-\s+|\s+—\s+", line, maxsplit=1)
                current = {
                    "title": parts[0].strip(),
                    "company": parts[1].strip() if len(parts) > 1 else "",
                    "start_date": None,
                    "end_date": None,
                    "is_current": False,
                    "responsibilities": [],
                    "achievements": [],
                }
                continue
            if current and len(line) <= 180 and not date_match:
                # A compact company/location line following a title.
                if not current.get("company") and not line.startswith(("•", "●", "▪", "◦")):
                    current["company"] = line
        if current and (current.get("company") or current.get("title")):
            entries.append(current)
        return [x for x in entries if x.get("title") and x.get("company")]

    def _extract_skills(self, text: str) -> List[Dict[str, Any]]:
        if not text.strip():
            return []
        raw = re.split(r"[,;|\n]", text)
        skills: List[Dict[str, Any]] = []
        seen = set()
        for item in raw:
            value = re.sub(r"^[•●▪◦*-]\s*", "", item).strip()
            if not value or len(value) > 80:
                continue
            low = value.lower()
            category = "Technical"
            for cat, keywords in self.skill_categories.items():
                if any(re.search(rf"(?<!\w){re.escape(k)}(?!\w)", low) for k in keywords):
                    category = cat
                    break
            key = low
            if key not in seen:
                seen.add(key)
                skills.append({"name": value, "category": category, "confidence": 0.8})
        return skills

    def _extract_certifications(self, text: str) -> List[Dict[str, Any]]:
        if not text.strip():
            return []
        certs: List[Dict[str, Any]] = []
        seen = set()
        for line in re.split(r"[,;\n]", text):
            value = re.sub(r"^[•●▪◦*-]\s*", "", line).strip()
            if not value or len(value) > 180:
                continue
            matched = next((cert for cert in self.known_certifications if re.search(rf"\b{re.escape(cert)}\b", value, re.I)), None)
            # In a certification section, allow a short credential name, but reject prose.
            if not matched and len(value.split()) > 12:
                continue
            name = matched or value
            key = name.lower()
            if key in seen:
                continue
            seen.add(key)
            issuer_match = re.search(r"(?:from|issued\s+by|issuer)\s*[:\-]?\s*([^,|]+)", value, re.I)
            date_match = re.search(r"\b(19|20)\d{2}\b", value)
            certs.append({
                "name": name,
                "issuer": issuer_match.group(1).strip() if issuer_match else "Unknown",
                "issue_date": date_match.group(0) if date_match else None,
                "confidence": 0.9 if matched else 0.7,
            })
        return certs

    def _extract_education(self, text: str) -> List[Dict[str, Any]]:
        if not text.strip():
            return []
        degree_re = re.compile(r"\b(?:PhD|Doctorate|DBA|DPhil|MBA|MCA|MSc|MS|MA|MEng|Master(?:'s)?|BBA|BCA|BSc|BS|BA|BEng|Bachelor(?:'s)?|Diploma|PGDM)\b[^\n,|;]*", re.I)
        institution_re = re.compile(r"\b(?:University|College|Institute|School|Academy)\b[^\n,|;]*", re.I)
        years = re.findall(r"\b(?:19|20)\d{2}\b", text)
        degree = degree_re.search(text)
        institution = institution_re.search(text)
        if not degree or not institution:
            return []
        return [{
            "degree": degree.group(0).strip(),
            "field": None,
            "institution": institution.group(0).strip(),
            "start_date": years[0] if len(years) > 1 else None,
            "end_date": years[1] if len(years) > 1 else (years[0] if years else None),
            "is_current": False,
            "confidence": 0.85,
        }]

    def _extract_projects(self, text: str) -> List[Dict[str, Any]]:
        if not text.strip():
            return []
        projects = []
        for line in text.splitlines():
            value = re.sub(r"^[•●▪◦*-]\s*", "", line).strip()
            if value and len(value) <= 220:
                projects.append({"name": value, "description": value, "confidence": 0.65})
        return projects[:25]

    def _extract_achievements(self, text: str) -> List[Dict[str, Any]]:
        if not text.strip():
            return []
        achievements = []
        for line in text.splitlines():
            value = re.sub(r"^[•●▪◦*-]\s*", "", line).strip()
            if value and len(value) <= 240:
                achievements.append({"description": value, "confidence": 0.7})
        return achievements[:25]

    @staticmethod
    def _calculate_confidence(sections: Dict[str, str]) -> float:
        expected = {"summary", "experience", "education", "certifications", "skills"}
        present = len(expected.intersection(sections.keys()))
        return round(min(0.45 + present * 0.1, 0.95), 2)
