import re
import json
from typing import Dict, List, Any, Optional
from datetime import datetime


class CVParser:
    """
    CV/Resume parser that extracts structured information.
    
    This is a foundation implementation. In production, this would
    be enhanced with more sophisticated NLP/ML models.
    """
    
    def __init__(self):
        # Common patterns for extraction
        self.patterns = {
            "email": r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            "phone": r'(\+\d{1,3}[\s-]?)?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{4}',
            "linkedin": r'(linkedin\.com/in/[\w-]+)',
            "url": r'https?://[^\s]+',
        }
        
        # Common job title indicators
        self.title_patterns = [
            r'job title[\s:]+([^\n]+)',
            r'position[\s:]+([^\n]+)',
            r'profile[\s:]+([^\n]+)',
            r'^([A-Z][a-z]+ (?:(?:Senior|Lead|Principal|Staff|Director|Manager|Architect|Engineer|Analyst|Consultant|Specialist|Expert)[\s-]?)+)',
        ]
        
        # Common skill categories
        self.skill_categories = {
            "Networking": ["routing", "switching", "BGP", "OSPF", "MPLS", "SD-WAN", "VLAN", "VPN"],
            "Security": ["firewall", "IPS", "IDS", "zero trust", "segmentation", "SIEM", "EDR", "DLP"],
            "Cloud": ["AWS", "Azure", "GCP", "cloud", "hybrid cloud", "multi-cloud"],
            "Infrastructure": ["server", "storage", "virtualization", "VMware", "Hyper-V", "Kubernetes", "Docker"],
            "Cybersecurity": ["threat", "vulnerability", "incident response", "malware"],
            "Automation": ["automation", "scripting", "CI/CD", "devops", "Ansible", "Terraform"],
            "Programming": ["Python", "Java", "Go", "Rust", "C++", "JavaScript", "TypeScript"],
            "Database": ["PostgreSQL", "MySQL", "MongoDB", "Redis", "Kafka", "Elasticsearch"],
            "Monitoring": ["Prometheus", "Grafana", "Datadog", "New Relic"],
        }
    
    def parse(self, text: str, document_id: Optional[str] = None) -> Dict[str, Any]:
        """Parse CV text and extract structured information."""
        
        result = {
            "personal": self._extract_personal(text),
            "professional": self._extract_professional(text),
            "skills": self._extract_skills(text),
            "certifications": self._extract_certifications(text),
            "education": self._extract_education(text),
            "projects": self._extract_projects(text),
            "achievements": self._extract_achievements(text),
            "raw_text": text[:5000] if len(text) > 5000 else text,  # Truncated for storage
            "confidence": self._calculate_confidence(text),
            "extracted_at": datetime.now().isoformat(),
            "version": "1.0"
        }
        
        return result
    
    def _extract_personal(self, text: str) -> Dict[str, Any]:
        """Extract personal information."""
        personal = {}
        
        # Extract name (first line or after "Name:")
        lines = text.split('\n')
        name_match = re.search(r'name[\s:]+([^\n]+)', text, re.IGNORECASE)
        if name_match:
            personal["name"] = name_match.group(1).strip()
        else:
            # Try first non-empty line (often the name)
            for line in lines[:5]:
                line = line.strip()
                if line and len(line) < 100 and not any(c in line for c in ['@', 'http', 'phone']):
                    personal["name"] = line
                    break
        
        # Extract email
        email_match = re.search(self.patterns["email"], text)
        if email_match:
            personal["email"] = email_match.group(0)
        
        # Extract phone
        phone_match = re.search(self.patterns["phone"], text)
        if phone_match:
            personal["phone"] = phone_match.group(0)
        
        # Extract LinkedIn
        linkedin_match = re.search(self.patterns["linkedin"], text, re.IGNORECASE)
        if linkedin_match:
            personal["linkedin"] = linkedin_match.group(0)
        
        # Extract location
        location_patterns = [
            r'location[\s:]+([^\n]+)',
            r'based in[\s:]+([^\n]+)',
        ]
        for pattern in location_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                personal["location"] = match.group(1).strip()
                break
        
        # Extract title
        for pattern in self.title_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                personal["title"] = match.group(1).strip()
                break
        
        # Extract summary (paragraph after name/title)
        summary_pattern = r'(?:summary|profile|about)[\s:]+([^\n]+(?:\n[^\n]+){0,5})'
        match = re.search(summary_pattern, text, re.IGNORECASE)
        if match:
            personal["summary"] = match.group(1).strip()
        
        return personal
    
    def _extract_professional(self, text: str) -> List[Dict[str, Any]]:
        """Extract professional experience."""
        experiences = []
        
        # Split by common experience sections
        experience_patterns = [
            r'experience[\s:]+([\s\S]+?)(?=(?:education|skills|certifications|$))',
            r'employment[\s:]+([\s\S]+?)(?=(?:education|skills|certifications|$))',
            r'work history[\s:]+([\s\S]+?)(?=(?:education|skills|certifications|$))',
        ]
        
        exp_text = text
        for pattern in experience_patterns:
            match = re.search(pattern, exp_text, re.IGNORECASE)
            if match:
                exp_text = match.group(1)
                break
        
        # Parse individual experiences
        lines = exp_text.split('\n')
        current_exp = {}
        in_experience = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this is a new experience (company + title pattern)
            company_match = re.search(r'^([A-Z][a-zA-Z\s]+(?:Inc|Corp|LLC|Ltd|Company|Technologies|Solutions|Systems|Group|Partners)[\s,.]?)', line)
            if company_match:
                if current_exp:
                    experiences.append(current_exp)
                current_exp = {
                    "company": company_match.group(1).strip(),
                    "title": "",
                    "start_date": None,
                    "end_date": None,
                    "responsibilities": [],
                    "achievements": []
                }
                in_experience = True
                # Check if title is also on this line
                remaining = line[len(company_match.group(0)):].strip()
                if remaining and "|" in remaining:
                    parts = remaining.split("|")
                    current_exp["title"] = parts[0].strip()
                continue
            
            # Check for title line
            title_match = re.search(r'^([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)\s+(?:-|–|—)\s+([A-Z][a-zA-Z\s]+(?:Inc|Corp|LLC|Ltd|Company|Technologies|Solutions|Systems))', line)
            if title_match:
                if current_exp:
                    experiences.append(current_exp)
                current_exp = {
                    "company": title_match.group(2).strip(),
                    "title": title_match.group(1).strip(),
                    "start_date": None,
                    "end_date": None,
                    "responsibilities": [],
                    "achievements": []
                }
                in_experience = True
                continue
            
            # Check for dates
            date_match = re.search(r'(\d{4})\s*[-–—]\s*(\d{4}|present)', line, re.IGNORECASE)
            if date_match and current_exp:
                current_exp["start_date"] = date_match.group(1)
                current_exp["end_date"] = date_match.group(2) if date_match.group(2).lower() != "present" else None
                if date_match.group(2).lower() == "present":
                    current_exp["is_current"] = True
                continue
            
            # Collect responsibilities and achievements
            if in_experience and current_exp and line.startswith(("•", "-", "*", "✓", "▶", "")):
                clean_line = line.lstrip("•-*✓▶ ").strip()
                if clean_line.startswith(("Achieved", "Delivered", "Led", "Managed", "Created", "Developed", "Improved", "Reduced")):
                    current_exp["achievements"].append(clean_line)
                else:
                    current_exp["responsibilities"].append(clean_line)
        
        if current_exp:
            experiences.append(current_exp)
        
        return experiences
    
    def _extract_skills(self, text: str) -> List[Dict[str, Any]]:
        """Extract skills from text."""
        skills = []
        skill_text = ""
        
        # Find skills section
        skill_section_match = re.search(r'(?:skills|technologies|competencies|expertise)[\s:]+([\s\S]+?)(?=(?:experience|education|certifications|$))', text, re.IGNORECASE)
        if skill_section_match:
            skill_text = skill_section_match.group(1)
        
        # If no skills section found, search for individual skills
        if not skill_text:
            # Look for skill keywords throughout the text
            all_skills = set()
            for category, keywords in self.skill_categories.items():
                for keyword in keywords:
                    if keyword.lower() in text.lower():
                        all_skills.add(keyword)
            for skill in all_skills:
                skills.append({"name": skill, "category": "Technical"})
            return skills
        
        # Parse skills from section
        skill_lines = re.split(r'[,\n]', skill_text)
        for line in skill_lines:
            line = line.strip()
            if line and len(line) < 100:
                # Check if skill belongs to a category
                category = "Technical"
                for cat, keywords in self.skill_categories.items():
                    if any(kw.lower() in line.lower() for kw in keywords):
                        category = cat
                        break
                skills.append({"name": line, "category": category})
        
        return skills
    
    def _extract_certifications(self, text: str) -> List[Dict[str, Any]]:
        """Extract certifications."""
        certifications = []
        
        # Find certifications section
        cert_section_match = re.search(r'(?:certifications|certificates|qualifications|credentials)[\s:]+([\s\S]+?)(?=(?:experience|education|skills|$))', text, re.IGNORECASE)
        if not cert_section_match:
            return certifications
        
        cert_text = cert_section_match.group(1)
        cert_lines = re.split(r'[,\n]', cert_text)
        
        common_certs = ["CISSP", "CISA", "CISM", "CRISC", "CCSP", "CCIE", "CCNP", "CCNA", 
                        "AWS", "Azure", "PMP", "ITIL", "TOGAF", "CEH", "OSCP", "CISSP-ISSAP"]
        
        for line in cert_lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if it's a known certification
            cert_name = None
            for cert in common_certs:
                if cert.lower() in line.lower():
                    cert_name = cert
                    break
            
            if not cert_name and len(line) < 50:
                cert_name = line
            
            if cert_name:
                # Try to extract issuer
                issuer_match = re.search(r'(?:from|issued by)\s+([^\n,]+)', line, re.IGNORECASE)
                issuer = issuer_match.group(1).strip() if issuer_match else None
                
                # Try to extract date
                date_match = re.search(r'(\d{4})', line)
                issue_date = date_match.group(1) if date_match else None
                
                certifications.append({
                    "name": cert_name,
                    "issuer": issuer or "Unknown",
                    "issue_date": issue_date,
                    "confidence": 0.7
                })
        
        return certifications
    
    def _extract_education(self, text: str) -> List[Dict[str, Any]]:
        """Extract education."""
        education = []
        
        # Find education section
        edu_section_match = re.search(r'(?:education|academic)[\s:]+([\s\S]+?)(?=(?:experience|skills|certifications|$))', text, re.IGNORECASE)
        if not edu_section_match:
            return education
        
        edu_text = edu_section_match.group(1)
        
        # Parse education entries
        degree_patterns = [
            r'(Bachelor|B\.?[A-Z]\.?|BA|BS|BSc|BEng|BBA)\s+(?:of|in)?\s*([^\n,]+)',
            r'(Master|M\.?[A-Z]\.?|MA|MS|MSc|MBA|MEng)\s+(?:of|in)?\s*([^\n,]+)',
            r'(PhD|Doctorate|DBA|DPhil)\s+(?:of|in)?\s*([^\n,]+)',
        ]
        
        lines = edu_text.split('\n')
        current_edu = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_edu:
                    education.append(current_edu)
                    current_edu = {}
                continue
            
            # Check for degree
            for pattern in degree_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    if current_edu:
                        education.append(current_edu)
                    current_edu = {
                        "degree": match.group(0).strip(),
                        "field": match.group(2) if len(match.groups()) > 1 else None,
                        "institution": None,
                        "start_date": None,
                        "end_date": None
                    }
                    # Check if institution is on same line
                    remaining = line[len(match.group(0)):].strip()
                    if remaining and not re.search(r'\d{4}', remaining):
                        current_edu["institution"] = remaining
                    break
            
            # Check for institution
            if not current_edu or not current_edu.get("institution"):
                institution_match = re.search(r'(University|College|Institute|School|Academy)[\s:]+([^\n,]+)', line, re.IGNORECASE)
                if institution_match:
                    current_edu["institution"] = institution_match.group(2).strip()
            
            # Check for dates
            date_match = re.search(r'(\d{4})\s*[-–—]\s*(\d{4}|present)', line, re.IGNORECASE)
            if date_match and current_edu:
                current_edu["start_date"] = date_match.group(1)
                current_edu["end_date"] = date_match.group(2) if date_match.group(2).lower() != "present" else None
                if date_match.group(2).lower() == "present":
                    current_edu["is_current"] = True
        
        if current_edu:
            education.append(current_edu)
        
        return education
    
    def _extract_projects(self, text: str) -> List[Dict[str, Any]]:
        """Extract projects."""
        projects = []
        
        # Find projects section
        project_section_match = re.search(r'(?:projects|initiatives)[\s:]+([\s\S]+?)(?=(?:experience|education|skills|certifications|$))', text, re.IGNORECASE)
        if not project_section_match:
            return projects
        
        project_text = project_section_match.group(1)
        
        # Parse projects
        lines = project_text.split('\n')
        current_project = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_project:
                    projects.append(current_project)
                    current_project = {}
                continue
            
            # Check if this is a project title
            if line and not line.startswith(("•", "-", "*", "✓", "▶")) and len(line) < 100:
                if current_project:
                    projects.append(current_project)
                current_project = {
                    "name": line,
                    "description": None,
                    "technologies": [],
                    "achievements": []
                }
            elif current_project:
                if line.startswith(("•", "-", "*", "✓", "▶")):
                    clean_line = line.lstrip("•-*✓▶ ").strip()
                    # Check if it's a technology mention
                    techs = []
                    for category, keywords in self.skill_categories.items():
                        for kw in keywords:
                            if kw.lower() in clean_line.lower():
                                techs.append(kw)
                    if techs:
                        current_project["technologies"].extend(techs)
                    else:
                        current_project["achievements"].append(clean_line)
                elif not current_project.get("description"):
                    current_project["description"] = line
        
        if current_project:
            projects.append(current_project)
        
        return projects
    
    def _extract_achievements(self, text: str) -> List[Dict[str, Any]]:
        """Extract achievements."""
        achievements = []
        
        # Look for achievement keywords
        achievement_keywords = ["achieved", "delivered", "led", "managed", "created", "developed", 
                               "improved", "reduced", "increased", "optimized", "transformed", 
                               "modernized", "architected", "designed", "implemented"]
        
        # Also look for bullet points with metrics
        bullet_pattern = r'[•\-*✓▶]\s*([^\n]+(?:achieved|delivered|led|managed|created|developed|improved|reduced|increased|optimized|transformed|modernized|architected|designed|implemented)[^\n]+)'
        
        matches = re.findall(bullet_pattern, text, re.IGNORECASE)
        for match in matches:
            # Check for metrics
            metric_match = re.search(r'(\d+%|\$\d+[\w,]+|\d+\+?)', match)
            achievements.append({
                "description": match.strip(),
                "metric": metric_match.group(0) if metric_match else None,
                "confidence": 0.6
            })
        
        return achievements
    
    def _calculate_confidence(self, text: str) -> float:
        """Calculate overall confidence score."""
        confidence = 0.5
        
        # Check if we found meaningful data
        if len(text) > 500:
            confidence += 0.1
        if re.search(r'[a-zA-Z]+\s+[a-zA-Z]+', text):  # Has names
            confidence += 0.1
        if re.search(r'\d{4}\s*[-–—]\s*\d{4}', text):  # Has dates
            confidence += 0.1
        if re.search(r'[•\-*✓▶]', text):  # Has bullet points
            confidence += 0.1
        if re.search(r'experience|education|skills', text, re.IGNORECASE):  # Has sections
            confidence += 0.1
        
        return min(confidence, 1.0)
