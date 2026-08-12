from typing import Dict, List, Any, Optional
from app.utils.jd_parser import JDParser


class JobDNAGenerator:
    """Generate Job DNA from parsed JD data."""
    
    def __init__(self):
        self.capability_mapping = {
            "network": "Network Architecture",
            "security": "Security Architecture",
            "cybersecurity": "Cyber Security",
            "cloud": "Cloud Architecture",
            "infrastructure": "Infrastructure Architecture",
            "automation": "Automation",
            "governance": "IT Governance",
            "risk": "Risk Management",
            "compliance": "Compliance",
            "leadership": "Strategic Leadership",
            "transformation": "Digital Transformation",
        }
    
    def generate(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Job DNA from parsed data."""
        
        # Extract capabilities from skills and responsibilities
        capabilities = self._extract_capabilities(parsed_data)
        
        # Build the Job DNA structure
        job_dna = {
            "role_family": self._determine_role_family(parsed_data),
            "seniority": parsed_data.get("seniority"),
            "capabilities": capabilities,
            "skills": self._extract_skill_dict(parsed_data.get("skills", [])),
            "mandatory_skills": self._extract_mandatory_skills(parsed_data.get("skills", [])),
            "preferred_skills": self._extract_preferred_skills(parsed_data.get("skills", [])),
            "technologies": self._extract_technologies(parsed_data.get("technologies", [])),
            "experience_requirements": {
                "minimum": parsed_data.get("experience_years"),
                "fields": ["engineering", "architecture"] if parsed_data.get("experience_years") else []
            },
            "architecture_domains": self._extract_domains(parsed_data),
            "leadership_scope": self._extract_leadership_scope(parsed_data),
            "governance_requirements": self._extract_governance(parsed_data),
            "industry": parsed_data.get("industry"),
            "location": {
                "location": parsed_data.get("location"),
                "remote_policy": parsed_data.get("remote_policy")
            },
            "mobility_requirements": {
                "relocation": parsed_data.get("relocation", False),
                "visa_sponsorship": parsed_data.get("visa_sponsorship", False)
            },
            "education_requirements": parsed_data.get("education", {}),
            "certifications_required": self._extract_certifications(parsed_data.get("certifications", [])),
            "summary": self._generate_summary(parsed_data),
            "keywords": self._extract_keywords(parsed_data),
            "confidence_score": self._calculate_confidence(parsed_data),
            "completeness_score": self._calculate_completeness(parsed_data),
        }
        
        return job_dna
    
    def _extract_capabilities(self, data: Dict) -> Dict[str, float]:
        """Extract capabilities from parsed data."""
        capabilities = {}
        
        # Check skills for capability indicators
        for skill in data.get("skills", []):
            skill_name = skill.get("name", "").lower()
            for key, capability in self.capability_mapping.items():
                if key in skill_name:
                    capabilities[capability] = 1.0
        
        # Add default capabilities based on role type
        if data.get("seniority") in ["manager", "director", "executive"]:
            capabilities["People Leadership"] = 1.0
            capabilities["Strategic Leadership"] = 1.0
        
        return capabilities
    
    def _determine_role_family(self, data: Dict) -> Optional[str]:
        """Determine the role family from parsed data."""
        title = data.get("title", "").lower()
        skills = [s.get("name", "").lower() for s in data.get("skills", [])]
        
        if "security" in title or any("security" in s for s in skills):
            return "Security Architect"
        elif "network" in title or any("network" in s for s in skills):
            return "Network Architect"
        elif "cloud" in title or any("cloud" in s for s in skills):
            return "Cloud Architect"
        elif "infrastructure" in title or any("infrastructure" in s for s in skills):
            return "Infrastructure Architect"
        elif any("cyber" in s for s in skills):
            return "Cyber Security Architect"
        elif any("manager" in s for s in skills):
            return "IT Manager"
        else:
            return "IT Professional"
    
    def _extract_skill_dict(self, skills: List[Dict]) -> Dict[str, str]:
        """Extract skills as dictionary."""
        return {s.get("name"): s.get("category", "Technical") for s in skills}
    
    def _extract_mandatory_skills(self, skills: List[Dict]) -> Dict[str, str]:
        """Extract mandatory skills."""
        mandatory = {}
        for s in skills:
            if s.get("is_mandatory", True):
                mandatory[s.get("name")] = s.get("category", "Technical")
        return mandatory
    
    def _extract_preferred_skills(self, skills: List[Dict]) -> Dict[str, str]:
        """Extract preferred skills."""
        preferred = {}
        for s in skills:
            if not s.get("is_mandatory", True):
                preferred[s.get("name")] = s.get("category", "Technical")
        return preferred
    
    def _extract_technologies(self, technologies: List[str]) -> List[str]:
        """Extract technologies list."""
        return technologies
    
    def _extract_domains(self, data: Dict) -> List[str]:
        """Extract architecture domains."""
        domains = []
        skills = [s.get("name", "").lower() for s in data.get("skills", [])]
        
        domain_mapping = {
            "network": "Network",
            "security": "Security",
            "cloud": "Cloud",
            "infrastructure": "Infrastructure",
            "enterprise": "Enterprise",
            "data": "Data",
            "application": "Application",
        }
        
        for key, domain in domain_mapping.items():
            if any(key in s for s in skills):
                domains.append(domain)
        
        return domains
    
    def _extract_leadership_scope(self, data: Dict) -> Dict[str, Any]:
        """Extract leadership scope."""
        scope = {"people": 0, "budget": 0, "strategic": False}
        
        seniority = data.get("seniority", "")
        if seniority == "executive":
            scope["people"] = 50
            scope["budget"] = 10000000
            scope["strategic"] = True
        elif seniority == "director":
            scope["people"] = 20
            scope["budget"] = 5000000
            scope["strategic"] = True
        elif seniority == "manager":
            scope["people"] = 5
            scope["budget"] = 1000000
            scope["strategic"] = False
        elif seniority == "senior":
            scope["people"] = 0
            scope["budget"] = 0
            scope["strategic"] = False
        
        return scope
    
    def _extract_governance(self, data: Dict) -> Dict[str, bool]:
        """Extract governance requirements."""
        governance = {"risk": False, "compliance": False, "policy": False}
        
        skills = [s.get("name", "").lower() for s in data.get("skills", [])]
        if "risk" in " ".join(skills):
            governance["risk"] = True
        if "compliance" in " ".join(skills):
            governance["compliance"] = True
        if "policy" in " ".join(skills):
            governance["policy"] = True
        
        return governance
    
    def _extract_certifications(self, certifications: List[str]) -> Dict[str, str]:
        """Extract certifications required."""
        return {cert: "required" for cert in certifications}
    
    def _generate_summary(self, data: Dict) -> str:
        """Generate a summary of the job."""
        title = data.get("title", "Unknown role")
        company = data.get("company", "Unknown company")
        seniority = data.get("seniority", "")
        
        summary = f"{seniority.capitalize()} position at {company}."
        if data.get("location"):
            summary += f" Based in {data['location']}."
        if data.get("remote_policy"):
            summary += f" {data['remote_policy']} work policy."
        
        return summary
    
    def _extract_keywords(self, data: Dict) -> List[str]:
        """Extract keywords from parsed data."""
        keywords = []
        if data.get("title"):
            keywords.extend(data["title"].split())
        for skill in data.get("skills", []):
            keywords.append(skill.get("name", ""))
        for tech in data.get("technologies", []):
            keywords.append(tech)
        return list(set(keywords))
    
    def _calculate_confidence(self, data: Dict) -> float:
        """Calculate confidence score (0-1)."""
        confidence = 0.5  # Start with base confidence
        
        # Increase confidence for each piece of data extracted
        if data.get("title"):
            confidence += 0.1
        if data.get("company"):
            confidence += 0.1
        if data.get("location") or data.get("remote_policy"):
            confidence += 0.1
        if data.get("skills"):
            confidence += 0.1
        if data.get("responsibilities"):
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _calculate_completeness(self, data: Dict) -> float:
        """Calculate completeness score (0-1)."""
        fields = ["title", "company", "location", "remote_policy", "skills", "responsibilities"]
        filled = sum(1 for field in fields if data.get(field))
        return filled / len(fields)
