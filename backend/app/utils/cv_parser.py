from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.utils.document_intelligence import segment_sections


class CVParser:
    """Precision-first career document parser.

    Domain fields are extracted only from the matching CV section, or from a document whose
    classifier explicitly identified it as that document type. This prevents skills, employers,
    and unrelated text from leaking into education/certifications.
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
    DEGREE_RE = re.compile(r"\b(Bachelor(?:'s)?|Master(?:'s)?|B\.?[A-Z]{1,4}\.?|M\.?[A-Z]{1,4}\.?|MBA|MSc|BSc|BEng|MEng|PhD|Doctorate|DBA|DPhil|Diploma)\b(?:\s+(?:of|in))?\s*([^,\n|]+)?", re.I)
    YEAR_RANGE_RE = re.compile(r"\b(19|20)(\d{2})\s*[-–—]\s*(?:(19|20)(\d{2})|present)\b", re.I)
    EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I)
    PHONE_RE = re.compile(r"(?:\+\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?)?\d{3,4}[\s.-]?\d{3,4}[\s.-]?\d{2,4}")

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
        return {
            "personal": personal,
            "professional": professional,
            "skills": skills,
            "certifications": certifications,
            "education": education,
            "projects": self._extract_projects(sections.get("projects", "")),
            "achievements": self._extract_achievements(sections.get("achievements", "")),
            "sections": sections,
            "source_document_id": document_id,
            "confidence": self._calculate_confidence(personal, professional, skills, certifications, education),
            "extracted_at": datetime.utcnow().isoformat(),
            "version": "2.0-section-aware",
        }

    def _extract_personal(self, text: str, sections: dict[str, str]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        lines = [x.strip() for x in text.splitlines() if x.strip()]
        for line in lines[:8]:
            if len(line) <= 80 and not self.EMAIL_RE.search(line) and not self.PHONE_RE.search(line) and "linkedin" not in line.lower() and not re.search(r"\b(resume|curriculum vitae|profile|summary)\b", line, re.I):
                result["name"] = line
                break
        email = self.EMAIL_RE.search(text)
        if email: result["email"] = email.group(0)
        phone = self.PHONE_RE.search(" ".join(lines[:15]))
        if phone: result["phone"] = phone.group(0).strip()
        linkedin = re.search(r"(?:https?://)?(?:www\.)?linkedin\.com/in/[A-Za-z0-9_-]+", text, re.I)
        if linkedin: result["linkedin"] = linkedin.group(0)
        for line in lines[:20]:
            if re.match(r"^(?:location|based in)\s*[:\-]", line, re.I): result["location"] = re.split(r"[:\-]", line, maxsplit=1)[1].strip()
            if re.match(r"^(?:title|current role|position)\s*[:\-]", line, re.I): result["title"] = re.split(r"[:\-]", line, maxsplit=1)[1].strip()
        if sections.get("summary"):
            result["summary"] = " ".join(x.strip() for x in sections["summary"].splitlines() if x.strip())[:4000]
        return result

    def _extract_professional(self, section: str) -> List[Dict[str, Any]]:
        if not section: return []
        entries: List[Dict[str, Any]] = []
        current: Dict[str, Any] | None = None
        for raw in section.splitlines():
            clean = raw.strip()
            if not clean: continue
            bullet = clean.lstrip("•-*✓▶ ").strip()
            date = self.YEAR_RANGE_RE.search(clean)
            # Common layouts: "Title | Company" or "Company - Title".
            pair = re.match(r"^(.{2,100}?)\s*(?:\||\bat\b|@)\s*(.{2,100})$", bullet, re.I)
            if not pair:
                pair = re.match(r"^(.{2,100}?)\s+[-–—]\s+(.{2,100})$", bullet)
            if pair and not date and len(bullet) < 220:
                if current and current.get("company") and current.get("title"): entries.append(current)
                left, right = pair.group(1).strip(), pair.group(2).strip()
                title_like = bool(re.search(r"\b(architect|engineer|manager|director|lead|consultant|analyst|specialist|executive|administrator|officer)\b", left, re.I))
                current = {"company": right if title_like else left, "title": left if title_like else right, "start_date": None, "end_date": None, "is_current": False, "responsibilities": [], "achievements": [], "confidence": 0.78}
                continue
            if current is None:
                if re.search(r"\b(architect|engineer|manager|director|lead|consultant|analyst|specialist|executive|administrator|officer)\b", bullet, re.I) and len(bullet) < 120:
                    current = {"company": "", "title": bullet, "start_date": None, "end_date": None, "is_current": False, "responsibilities": [], "achievements": [], "confidence": 0.62}
                continue
            if date:
                self._apply_dates(current, date); continue
            if not current.get("company") and len(bullet) < 120 and not bullet.endswith("."):
                current["company"] = bullet; continue
            if raw.strip().startswith(("•", "-", "*", "✓", "▶", "")) or len(bullet) > 35:
                (current["achievements"] if self._looks_like_achievement(bullet) else current["responsibilities"]).append(bullet)
        if current and current.get("company") and current.get("title"): entries.append(current)
        return entries

    def _extract_employment_document(self, text: str) -> List[Dict[str, Any]]:
        company = self._label(text, ["company", "employer", "organization"])
        title = self._label(text, ["designation", "job title", "position", "role"])
        if not company: return []
        item = {"company": company, "title": title or "Employment record", "start_date": None, "end_date": None, "is_current": False, "responsibilities": [], "achievements": [], "confidence": 0.65}
        m = self.YEAR_RANGE_RE.search(text)
        if m: self._apply_dates(item, m)
        return [item]

    def _extract_skills(self, section: str) -> List[Dict[str, Any]]:
        if not section: return []
        result=[]; seen=set()
        for raw in re.split(r"[,|;\n]", section):
            value=re.sub(r"^\s*[-•*]+\s*", "", raw).strip()
            if not value or len(value)>100 or len(value.split())>12: continue
            key=self._norm(value)
            if key in seen: continue
            seen.add(key)
            category="Technical"
            for cat, words in self.SKILLS.items():
                if any(re.search(rf"\b{re.escape(word)}\b", value, re.I) for word in words): category=cat; break
            result.append({"name":value,"category":category,"confidence":0.82})
        return result

    def _extract_certifications(self, section: str) -> List[Dict[str, Any]]:
        if not section: return []
        result=[]; seen=set()
        for raw in re.split(r"[,|\n]", section):
            line=re.sub(r"^\s*[-•*]+\s*", "", raw).strip()
            if not line or len(line)>180: continue
            explicit=bool(re.search(r"\b(certified|certification|credential|license|professional certificate)\b", line, re.I))
            known=bool(re.search(r"\b(CISSP|CISA|CISM|CRISC|CCSP|CCIE|CCNP|CCNA|PMP|ITIL|TOGAF|CEH|OSCP)\b", line, re.I))
            if not explicit and not known: continue
            key=self._norm(line)
            if key in seen: continue
            seen.add(key)
            result.append({"name":line,"issuer":self._label(line,["issuer","issued by","from"]) or "Unknown","issue_date":self._year(line),"confidence":0.88})
        return result

    def _extract_certification_document(self, text: str) -> List[Dict[str, Any]]:
        name=self._label(text,["certification","certificate","credential","certification name"])
        if not name:
            for pattern in (r"(?:is hereby|has been awarded|successfully completed)\s+(?:the\s+)?(.{4,160}?(?:certification|certificate|credential))",r"(AWS Certified [^\n]+)",r"(Microsoft Certified [^\n]+)"):
                m=re.search(pattern,text,re.I)
                if m: name=m.group(1).strip(); break
        if not name: return []
        return [{"name":name[:255],"issuer":(self._label(text,["issuer","issued by","organization","awarded by"]) or "Unknown")[:255],"credential_reference":self._label(text,["credential id","credential number","certificate number","license number"]),"issue_date":self._year(text),"expiry_date":self._expiry(text),"confidence":0.93}]

    def _extract_education(self, section: str) -> List[Dict[str, Any]]:
        if not section: return []
        result=[]
        for block in re.split(r"\n\s*\n", section):
            m=self.DEGREE_RE.search(block)
            if not m: continue
            degree=m.group(0).strip(); field=(m.group(2) or "").strip() or None
            institution=None
            for line in block.splitlines():
                clean=line.strip()
                if re.search(r"\b(University|College|Institute|School|Academy)\b",clean,re.I): institution=re.sub(r"\s*[,|].*$", "", clean).strip(); break
            if not institution: continue
            dates=self.YEAR_RANGE_RE.search(block); tmp={}
            if dates: self._apply_dates(tmp,dates)
            result.append({"degree":degree[:255],"field":field,"institution":institution[:255],"start_date":tmp.get("start_date"),"end_date":tmp.get("end_date"),"confidence":0.9})
        return result

    def _extract_education_document(self, text: str) -> List[Dict[str, Any]]:
        m=self.DEGREE_RE.search(text)
        if not m: return []
        institution=self._label(text,["institution","university","college","school","institute"])
        if not institution:
            im=re.search(r"\b((?:University|College|Institute|School|Academy)\s+of\s+[A-Z][A-Za-z &.-]+|[A-Z][A-Za-z &.-]+\s+(?:University|College|Institute|School|Academy))",text)
            institution=im.group(1).strip() if im else None
        if not institution: return []
        return [{"degree":m.group(0).strip()[:255],"field":(m.group(2) or "").strip() or None,"institution":institution[:255],"start_date":None,"end_date":self._year(text),"confidence":0.92}]

    def _extract_achievements(self, section: str) -> List[str]:
        return [re.sub(r"^\s*[-•*✓▶]+\s*", "", x).strip() for x in section.splitlines() if x.strip() and self._looks_like_achievement(x)]

    def _extract_projects(self, section: str) -> List[Dict[str, Any]]:
        return [{"name":re.sub(r"^\s*[-•*]+\s*", "", x).strip()} for x in section.splitlines() if x.strip()][:50]

    def _looks_like_achievement(self,text:str)->bool:
        return bool(re.search(r"\b(increased|reduced|delivered|achieved|saved|grew|improved|led|launched|migrated|transformed|built|created|won)\b|\b\d+%\b|\$\s?\d",text,re.I))

    def _apply_dates(self,target:Dict[str,Any],match:re.Match)->None:
        start=f"{match.group(1)}{match.group(2)}"; end=match.group(3)+match.group(4) if match.group(4) else None
        target["start_date"]=f"{start}-01-01"; target["end_date"]=None if not end else f"{end}-12-31"; target["is_current"]=not bool(end)

    def _label(self,text:str,labels:list[str])->str|None:
        for label in labels:
            m=re.search(rf"{re.escape(label)}\s*[:\-]\s*([^\n]+)",text,re.I)
            if m:return m.group(1).strip()
        return None

    def _year(self,text:str)->str|None:
        m=re.search(r"\b(19|20)\d{2}\b",text)
        return m.group(0) if m else None

    def _expiry(self,text:str)->str|None:
        m=re.search(r"(?:expiry|expires|valid until)\s*[:\-]?\s*(\d{4})",text,re.I)
        return m.group(1) if m else None

    def _norm(self,value:str)->str:
        return re.sub(r"[^a-z0-9]+"," ",value.lower()).strip()

    def _calculate_confidence(self,personal,professional,skills,certifications,education)->float:
        return round(min(0.98,0.45+0.11*sum(bool(x) for x in (personal,professional,skills,certifications,education))),2)
