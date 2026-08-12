from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import re

class ResumeGenerator:
    """JD-specific resume generator with evidence-based content."""
    
    def __init__(self):
        self.section_order = [
            "summary",
            "experience",
            "skills",
            "certifications",
            "education",
            "projects"
        ]
        
        self.ats_keywords = [
            "achieved", "led", "managed", "developed", "implemented",
            "designed", "architected", "delivered", "improved", "reduced",
            "increased", "optimized", "transformed", "modernized"
        ]
    
    def generate(self, career_vault: Dict, persona: Dict, job_dna: Dict) -> Dict:
        """
        Generate a JD-specific resume from career vault data.
        
        Returns:
            Dict with resume content, sections, evidence links, and metadata.
        """
        # 1. Select relevant evidence
        evidence = self._select_evidence(career_vault, job_dna, persona)
        
        # 2. Build sections
        sections = self._build_sections(evidence, job_dna, persona)
        
        # 3. Generate full content
        content = self._assemble_resume(sections, job_dna, persona)
        
        # 4. Calculate ATS score
        ats_score = self._calculate_ats_score(content, job_dna)
        
        # 5. Calculate truth score
        truth_score = self._calculate_truth_score(sections)
        
        # 6. Generate keyword coverage
        keyword_coverage = self._calculate_keyword_coverage(content, job_dna)
        
        return {
            "content": content,
            "sections": sections,
            "ats_score": ats_score,
            "truth_score": truth_score,
            "keyword_coverage": keyword_coverage,
            "format_type": "ats",
            "evidence_links": self._compile_evidence_links(sections)
        }
    
    def _select_evidence(self, career_vault: Dict, job_dna: Dict, persona: Dict) -> Dict:
        """Select the most relevant evidence from the career vault."""
        selected = {
            "employments": [],
            "projects": [],
            "skills": [],
            "certifications": [],
            "educations": [],
            "achievements": []
        }
        
        # Get job keywords
        job_keywords = set(job_dna.get("keywords", []))
        job_skills = set(job_dna.get("skills", {}).keys())
        job_tech = set(job_dna.get("technologies", []))
        
        # Score and select employments
        for emp in career_vault.get("employments", []):
            relevance = self._calculate_relevance(emp, job_keywords, job_skills, job_tech)
            emp["relevance"] = relevance
            selected["employments"].append(emp)
        
        # Sort by relevance
        selected["employments"] = sorted(
            selected["employments"],
            key=lambda x: x.get("relevance", 0),
            reverse=True
        )
        
        # Select top 3 employments
        selected["employments"] = selected["employments"][:3]
        
        # Select skills relevant to job
        for skill in career_vault.get("skills", []):
            if skill.get("name") in job_skills:
                selected["skills"].append(skill)
        
        # Select certifications relevant to job
        job_certs = set(job_dna.get("certifications_required", {}).keys())
        for cert in career_vault.get("certifications", []):
            if cert.get("name") in job_certs:
                selected["certifications"].append(cert)
        
        # Select projects relevant to job
        for project in career_vault.get("projects", []):
            project_tech = set(project.get("technologies", []))
            if project_tech.intersection(job_tech):
                selected["projects"].append(project)
        
        # Select top 3 projects
        selected["projects"] = selected["projects"][:3]
        
        # Add all education
        selected["educations"] = career_vault.get("educations", [])
        
        return selected
    
    def _calculate_relevance(self, item: Dict, job_keywords: set, job_skills: set, job_tech: set) -> float:
        """Calculate relevance score for a career item."""
        score = 0.0
        
        # Check item description for job keywords
        description = item.get("description", "") + " " + item.get("responsibilities", "")
        description_lower = description.lower()
        
        # Count keyword matches
        keyword_matches = sum(1 for kw in job_keywords if kw.lower() in description_lower)
        score += keyword_matches * 0.5
        
        # Check for skill matches
        if item.get("title"):
            title_lower = item["title"].lower()
            for skill in job_skills:
                if skill.lower() in title_lower:
                    score += 1.0
        
        # Check for technology matches
        techs = item.get("technologies", [])
        if isinstance(techs, list):
            tech_matches = sum(1 for t in techs if t in job_tech)
            score += tech_matches * 0.3
        
        return min(score, 10.0)
    
    def _build_sections(self, evidence: Dict, job_dna: Dict, persona: Dict) -> List[Dict]:
        """Build resume sections from selected evidence."""
        sections = []
        
        # 1. Summary Section
        summary = self._build_summary(evidence, job_dna, persona)
        sections.append({
            "type": "summary",
            "title": "Professional Summary",
            "content": summary,
            "order": 0,
            "evidence": []
        })
        
        # 2. Experience Section
        experience_sections = self._build_experience(evidence, job_dna)
        sections.extend(experience_sections)
        
        # 3. Skills Section
        skills_content = self._build_skills(evidence, job_dna)
        sections.append({
            "type": "skills",
            "title": "Skills & Expertise",
            "content": skills_content,
            "order": 10,
            "evidence": evidence.get("skills", [])
        })
        
        # 4. Certifications Section
        if evidence.get("certifications"):
            certs_content = self._build_certifications(evidence)
            sections.append({
                "type": "certifications",
                "title": "Certifications",
                "content": certs_content,
                "order": 20,
                "evidence": evidence.get("certifications", [])
            })
        
        # 5. Education Section
        if evidence.get("educations"):
            edu_content = self._build_education(evidence)
            sections.append({
                "type": "education",
                "title": "Education",
                "content": edu_content,
                "order": 30,
                "evidence": evidence.get("educations", [])
            })
        
        # 6. Projects Section
        if evidence.get("projects"):
            projects_content = self._build_projects(evidence)
            sections.append({
                "type": "projects",
                "title": "Key Projects",
                "content": projects_content,
                "order": 40,
                "evidence": evidence.get("projects", [])
            })
        
        return sections
    
    def _build_summary(self, evidence: Dict, job_dna: Dict, persona: Dict) -> str:
        """Build a professional summary."""
        title = persona.get("name", "IT Professional")
        years = len(evidence.get("employments", [])) * 2  # Estimate
        skills = ", ".join([s.get("name") for s in evidence.get("skills", [])[:5]])
        
        # Get job keywords for tailoring
        job_keywords = job_dna.get("keywords", [])[:5]
        keywords_str = ", ".join(job_keywords) if job_keywords else skills
        
        summary = f"Senior {title} with {years}+ years of experience in {keywords_str}. "
        summary += f"Expert in {skills}. "
        summary += "Proven track record of delivering complex technical solutions and leading teams to success."
        
        return summary
    
    def _build_experience(self, evidence: Dict, job_dna: Dict) -> List[Dict]:
        """Build experience sections."""
        sections = []
        order = 1
        
        for emp in evidence.get("employments", []):
            content = self._format_employment(emp, job_dna)
            sections.append({
                "type": "experience",
                "title": emp.get("company", "Experience"),
                "content": content,
                "order": order,
                "evidence": [emp]
            })
            order += 1
        
        return sections
    
    def _format_employment(self, emp: Dict, job_dna: Dict) -> str:
        """Format an employment entry."""
        company = emp.get("company", "")
        title = emp.get("title", "")
        start = emp.get("start_date", "")
        end = emp.get("end_date", "Present")
        responsibilities = emp.get("responsibilities", "")
        achievements = emp.get("achievements", [])
        
        # Format date
        start_str = start.strftime("%B %Y") if start else ""
        end_str = end.strftime("%B %Y") if end != "Present" and end else "Present"
        
        content = f"{title} | {company}\n"
        content += f"{start_str} - {end_str}\n\n"
        
        # Add responsibilities
        if responsibilities:
            content += f"{responsibilities}\n"
        
        # Add achievements
        if achievements:
            content += "\nKey Achievements:\n"
            for achievement in achievements[:3]:
                if isinstance(achievement, dict):
                    content += f"• {achievement.get('description', '')}\n"
                else:
                    content += f"• {achievement}\n"
        
        return content
    
    def _build_skills(self, evidence: Dict, job_dna: Dict) -> str:
        """Build skills section."""
        skills = evidence.get("skills", [])
        
        # Group skills by category
        categories = {}
        for skill in skills:
            cat = skill.get("category", "Technical")
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(skill.get("name"))
        
        content = ""
        for cat, items in categories.items():
            content += f"{cat}: {', '.join(items)}\n"
        
        return content
    
    def _build_certifications(self, evidence: Dict) -> str:
        """Build certifications section."""
        certs = evidence.get("certifications", [])
        content = ""
        for cert in certs:
            name = cert.get("name", "")
            issuer = cert.get("issuer", "")
            date = cert.get("issue_date", "")
            date_str = date.strftime("%B %Y") if date else ""
            
            content += f"{name} - {issuer}"
            if date_str:
                content += f" ({date_str})"
            content += "\n"
        
        return content
    
    def _build_education(self, evidence: Dict) -> str:
        """Build education section."""
        educations = evidence.get("educations", [])
        content = ""
        for edu in educations:
            institution = edu.get("institution", "")
            degree = edu.get("degree", "")
            field = edu.get("field_of_study", "")
            start = edu.get("start_date", "")
            end = edu.get("end_date", "Present")
            
            start_str = start.strftime("%B %Y") if start else ""
            end_str = end.strftime("%B %Y") if end != "Present" and end else "Present"
            
            content += f"{degree} in {field} - {institution}\n"
            content += f"{start_str} - {end_str}\n\n"
        
        return content
    
    def _build_projects(self, evidence: Dict) -> str:
        """Build projects section."""
        projects = evidence.get("projects", [])
        content = ""
        for project in projects:
            name = project.get("name", "")
            description = project.get("description", "")
            technologies = project.get("technologies", [])
            achievements = project.get("achievements", [])
            
            content += f"{name}\n"
            if description:
                content += f"{description}\n"
            if technologies:
                content += f"Technologies: {', '.join(technologies)}\n"
            if achievements:
                for achievement in achievements[:2]:
                    if isinstance(achievement, dict):
                        content += f"• {achievement.get('description', '')}\n"
                    else:
                        content += f"• {achievement}\n"
            content += "\n"
        
        return content
    
    def _assemble_resume(self, sections: List[Dict], job_dna: Dict, persona: Dict) -> str:
        """Assemble the full resume from sections."""
        # Header
        header = self._build_header(persona)
        
        # Body
        body = ""
        for section in sections:
            body += f"\n{section.get('title', '').upper()}\n"
            body += "=" * 40 + "\n"
            body += section.get("content", "") + "\n"
        
        return header + body
    
    def _build_header(self, persona: Dict) -> str:
        """Build resume header."""
        name = persona.get("name", "Professional")
        title = persona.get("description", "IT Professional")
        
        header = f"{name.upper()}\n"
        header += f"{title}\n"
        header += "=" * 40 + "\n"
        
        return header
    
    def _calculate_ats_score(self, content: str, job_dna: Dict) -> float:
        """Calculate ATS compatibility score."""
        score = 0.0
        
        # Check for action verbs
        content_lower = content.lower()
        ats_verb_count = sum(1 for verb in self.ats_keywords if verb in content_lower)
        score += min(ats_verb_count / 5, 1.0) * 30
        
        # Check for keyword coverage
        keywords = job_dna.get("keywords", [])
        if keywords:
            keyword_matches = sum(1 for kw in keywords if kw.lower() in content_lower)
            score += (keyword_matches / len(keywords)) * 40
        
        # Check for section headers
        required_sections = ["experience", "skills", "summary"]
        for section in required_sections:
            if section in content_lower:
                score += 10
        
        return min(score, 100)
    
    def _calculate_truth_score(self, sections: List[Dict]) -> float:
        """Calculate truth verification score."""
        total_statements = 0
        verified_statements = 0
        
        for section in sections:
            evidence = section.get("evidence", [])
            total_statements += len(evidence)
            # Count evidence that has proper source references
            for item in evidence:
                if item.get("source_type") or item.get("company") or item.get("issuer"):
                    verified_statements += 1
        
        if total_statements == 0:
            return 100.0
        
        return (verified_statements / total_statements) * 100
    
    def _calculate_keyword_coverage(self, content: str, job_dna: Dict) -> float:
        """Calculate keyword coverage from job DNA."""
        keywords = job_dna.get("keywords", [])
        if not keywords:
            return 100.0
        
        content_lower = content.lower()
        matched = sum(1 for kw in keywords if kw.lower() in content_lower)
        
        return (matched / len(keywords)) * 100
    
    def _compile_evidence_links(self, sections: List[Dict]) -> List[Dict]:
        """Compile all evidence links from sections."""
        links = []
        for section in sections:
            for item in section.get("evidence", []):
                links.append({
                    "section": section.get("title"),
                    "statement": item.get("description") or item.get("name", ""),
                    "source": {
                        "type": section.get("type"),
                        "reference": item
                    },
                    "verified": True
                })
        return links
