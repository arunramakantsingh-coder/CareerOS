import re
from typing import Dict, List, Any, Optional
from datetime import datetime

class JDParser:
    """Parse raw job description into structured data."""
    
    def __init__(self):
        self.skill_patterns = {
            "network": ["routing", "switching", "SD-WAN", "LAN", "WAN", "BGP", "OSPF", "MPLS"],
            "security": ["firewall", "IPS", "IDS", "zero trust", "segmentation", "SIEM", "EDR"],
            "cloud": ["AWS", "Azure", "GCP", "cloud", "hybrid cloud", "multi-cloud"],
            "infrastructure": ["server", "storage", "virtualization", "VMware", "Hyper-V"],
            "cybersecurity": ["threat", "vulnerability", "incident response", "cybersecurity"],
            "automation": ["automation", "scripting", "CI/CD", "devops", "Ansible", "Terraform"],
        }
        
        self.seniority_patterns = {
            "executive": ["executive", "chief", "CXO", "C-level"],
            "director": ["director", "head of"],
            "manager": ["manager", "lead", "team lead"],
            "senior": ["senior", "sr."],
            "mid": ["mid-level", "experienced"],
            "entry": ["junior", "entry", "associate"],
        }
        
        self.remote_patterns = ["remote", "hybrid", "on-site", "onsite", "on site"]
    
    def parse(self, raw_jd: str) -> Dict[str, Any]:
        """Parse raw job description and extract structured information."""
        result = {
            "title": self._extract_title(raw_jd),
            "company": self._extract_company(raw_jd),
            "location": self._extract_location(raw_jd),
            "remote_policy": self._extract_remote_policy(raw_jd),
            "salary": self._extract_salary(raw_jd),
            "seniority": self._extract_seniority(raw_jd),
            "skills": self._extract_skills(raw_jd),
            "technologies": self._extract_technologies(raw_jd),
            "responsibilities": self._extract_responsibilities(raw_jd),
            "experience_years": self._extract_experience_years(raw_jd),
            "certifications": self._extract_certifications(raw_jd),
            "education": self._extract_education(raw_jd),
            "visa_sponsorship": self._extract_visa_sponsorship(raw_jd),
            "relocation": self._extract_relocation(raw_jd),
            "industry": self._extract_industry(raw_jd),
        }
        return result
    
    def _extract_title(self, text: str) -> Optional[str]:
        """Extract job title."""
        # Look for common patterns
        lines = text.split('\n')
        for i, line in enumerate(lines[:10]):  # Check first 10 lines
            line = line.strip()
            if any(word in line.lower() for word in ["job title", "position", "role"]):
                return line.split(":")[-1].strip() if ":" in line else line
            if len(line) < 100 and not line.startswith("http"):
                return line
        return None
    
    def _extract_company(self, text: str) -> Optional[str]:
        """Extract company name."""
        lines = text.split('\n')
        for line in lines[:15]:
            if "company" in line.lower() or "organization" in line.lower() or "about us" in line.lower():
                if ":" in line:
                    return line.split(":")[-1].strip()
        return None
    
    def _extract_location(self, text: str) -> Optional[str]:
        """Extract location."""
        location_patterns = [
            r"Location\s*:\s*([^\n]+)",
            r"location\s+([^\n]+)",
            r"Based in\s+([^\n]+)",
        ]
        for pattern in location_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None
    
    def _extract_remote_policy(self, text: str) -> Optional[str]:
        """Extract remote policy."""
        text_lower = text.lower()
        if "remote" in text_lower and ("fully remote" in text_lower or "100% remote" in text_lower):
            return "Remote"
        elif "hybrid" in text_lower:
            return "Hybrid"
        elif "on-site" in text_lower or "onsite" in text_lower:
            return "On-site"
        return None
    
    def _extract_salary(self, text: str) -> Dict[str, Any]:
        """Extract salary information."""
        result = {"min": None, "max": None, "currency": None}
        
        # Look for salary patterns
        salary_patterns = [
            r"(\$|\€|\£|₹)\s*([\d,]+)\s*-\s*(\$|\€|\£|₹)\s*([\d,]+)",
            r"(\d+)\s*-\s*(\d+)\s*(k|K)",
        ]
        
        for pattern in salary_patterns:
            match = re.search(pattern, text)
            if match:
                if len(match.groups()) == 4:
                    result["currency"] = match.group(1)
                    result["min"] = float(match.group(2).replace(",", ""))
                    result["max"] = float(match.group(4).replace(",", ""))
                elif len(match.groups()) == 3:
                    result["min"] = float(match.group(1)) * 1000
                    result["max"] = float(match.group(2)) * 1000
                    result["currency"] = "USD"
                break
        
        return result
    
    def _extract_seniority(self, text: str) -> Optional[str]:
        """Extract seniority level."""
        text_lower = text.lower()
        for level, keywords in self.seniority_patterns.items():
            if any(kw in text_lower for kw in keywords):
                return level
        return None
    
    def _extract_skills(self, text: str) -> List[Dict[str, Any]]:
        """Extract skills from JD."""
        skills = []
        text_lower = text.lower()
        
        for category, patterns in self.skill_patterns.items():
            for pattern in patterns:
                if pattern.lower() in text_lower:
                    skills.append({
                        "name": pattern,
                        "category": category,
                        "is_mandatory": True,  # Default assumption
                    })
        
        return skills
    
    def _extract_technologies(self, text: str) -> List[str]:
        """Extract technologies."""
        tech_list = []
        tech_patterns = [
            "AWS", "Azure", "GCP", "Kubernetes", "Docker", "Terraform",
            "Ansible", "Jenkins", "Python", "Java", "Go", "React",
            "Angular", "Node.js", "PostgreSQL", "MySQL", "MongoDB",
            "Redis", "Kafka", "Elasticsearch", "Prometheus", "Grafana",
        ]
        
        for tech in tech_patterns:
            if tech.lower() in text.lower():
                tech_list.append(tech)
        
        return tech_list
    
    def _extract_responsibilities(self, text: str) -> List[str]:
        """Extract responsibilities."""
        responsibilities = []
        
        # Look for bullet points or numbered lists
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith(("•", "-", "*", "✓", "▶")):
                responsibilities.append(line.lstrip("•-*✓▶ ").strip())
            elif re.match(r'^\d+\.', line):
                responsibilities.append(re.sub(r'^\d+\.\s*', '', line))
        
        return responsibilities
    
    def _extract_experience_years(self, text: str) -> Optional[int]:
        """Extract required years of experience."""
        patterns = [
            r"(\d+)\s*\+\s*years",
            r"(\d+)\s*years? of experience",
            r"experience\s*:\s*(\d+)\s*years",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        return None
    
    def _extract_certifications(self, text: str) -> List[str]:
        """Extract certifications."""
        certs = []
        cert_patterns = [
            "CISSP", "CISA", "CISM", "CRISC", "CCSP",
            "CCIE", "CCNP", "CCNA", "AWS Certified", "Azure Certified",
            "PMP", "ITIL", "TOGAF", "CEH", "OSCP",
        ]
        for cert in cert_patterns:
            if cert.lower() in text.lower():
                certs.append(cert)
        return certs
    
    def _extract_education(self, text: str) -> Dict[str, str]:
        """Extract education requirements."""
        result = {"degree": None, "field": None}
        degree_patterns = {
            "Bachelor": ["bachelor", "bs", "ba"],
            "Master": ["master", "ms", "ma", "mba"],
            "Doctorate": ["phd", "doctorate", "dba"],
        }
        text_lower = text.lower()
        for degree, keywords in degree_patterns.items():
            if any(kw in text_lower for kw in keywords):
                result["degree"] = degree
                break
        
        # Extract field
        field_patterns = [
            r"in\s+(computer science|information technology|engineering|business administration|cybersecurity)",
            r"computer science",
            r"information technology",
            r"engineering",
        ]
        for pattern in field_patterns:
            match = re.search(pattern, text_lower)
            if match:
                result["field"] = match.group(1) if match.groups() else pattern
                break
        
        return result
    
    def _extract_visa_sponsorship(self, text: str) -> bool:
        """Extract visa sponsorship indicator."""
        text_lower = text.lower()
        if "sponsor" in text_lower or "visa" in text_lower:
            if "no sponsorship" not in text_lower:
                return True
        return False
    
    def _extract_relocation(self, text: str) -> bool:
        """Extract relocation indicator."""
        text_lower = text.lower()
        if "relocation" in text_lower and "no relocation" not in text_lower:
            if "relocation assistance" in text_lower or "relocation package" in text_lower:
                return True
        return False
    
    def _extract_industry(self, text: str) -> Optional[str]:
        """Extract industry."""
        industries = {
            "financial services": ["banking", "finance", "insurance", "investment"],
            "technology": ["software", "tech", "IT", "internet"],
            "healthcare": ["healthcare", "medical", "pharmaceutical"],
            "telecommunications": ["telecom", "mobile", "broadband"],
            "consulting": ["consulting", "advisory"],
            "retail": ["retail", "e-commerce", "consumer"],
        }
        text_lower = text.lower()
        for industry, keywords in industries.items():
            if any(kw in text_lower for kw in keywords):
                return industry
        return None
