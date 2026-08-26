from typing import Dict, List, Any, Optional, Tuple
import math
from collections import defaultdict

class SemanticDiscoveryEngine:
    """
    Semantic Job Discovery Engine.
    
    Finds jobs based on career capabilities, skills, responsibilities,
    and architecture domains - NOT just job titles.
    """
    
    def __init__(self):
        # Weights for discovery scoring
        self.discovery_weights = {
            "capability_match": 0.30,
            "skill_match": 0.25,
            "responsibility_match": 0.20,
            "career_match": 0.15,
            "title_match": 0.10,
        }
        
        # Capability synonyms for semantic matching
        self.capability_synonyms = {
            "Network Architecture": ["network design", "network engineer", "network architect"],
            "Security Architecture": ["security design", "security engineer", "security architect"],
            "Cyber Security": ["cyber", "cybersecurity", "information security"],
            "Cloud Architecture": ["cloud", "aws", "azure", "gcp", "cloud engineer"],
            "Infrastructure Architecture": ["infrastructure", "system architect", "infrastructure engineer"],
            "Automation": ["automation", "devops", "ci/cd", "terraform"],
            "IT Governance": ["governance", "compliance", "policy"],
            "Risk Management": ["risk", "security risk", "operational risk"],
            "Strategic Leadership": ["strategy", "executive", "leadership"],
            "Digital Transformation": ["transformation", "modernization", "innovation"],
        }
    
    def discover(self, career_profile: Dict, persona: Dict, jobs: List[Dict]) -> List[Dict]:
        """
        Discover jobs that semantically match the career profile.
        
        Returns jobs ranked by semantic fit, not title similarity.
        """
        discoveries = []
        
        # Extract career capabilities
        career_capabilities = self._extract_career_capabilities(career_profile, persona)
        
        # Extract career skills
        career_skills = self._extract_career_skills(career_profile, persona)
        
        # Extract career responsibilities
        career_responsibilities = self._extract_career_responsibilities(career_profile)
        
        # Process each job
        for job in jobs:
            discovery = self._score_job(
                job,
                career_capabilities,
                career_skills,
                career_responsibilities,
                persona
            )
            discoveries.append(discovery)
        
        # Rank by overall score (semantic fit, not title similarity)
        discoveries.sort(key=lambda x: x["overall_score"], reverse=True)
        
        # Add rank
        for i, discovery in enumerate(discoveries):
            discovery["discovery_rank"] = i + 1
        
        return discoveries
    
    def _score_job(self, job: Dict, career_capabilities: List[str], 
                   career_skills: List[str], career_responsibilities: List[str],
                   persona: Dict) -> Dict:
        """Score a single job against the career profile."""
        
        # Extract job DNA
        job_dna = job.get("job_dna", {})
        job_skills = job_dna.get("skills", {})
        job_capabilities = job_dna.get("capabilities", {})
        job_responsibilities = job_dna.get("responsibilities", [])
        job_title = job.get("title", "")
        
        # 1. Capability Match (30%)
        capability_score, capability_details = self._match_capabilities(
            career_capabilities,
            job_capabilities
        )
        
        # 2. Skill Match (25%)
        skill_score, skill_details = self._match_skills(
            career_skills,
            job_skills
        )
        
        # 3. Responsibility Match (20%)
        responsibility_score, responsibility_details = self._match_responsibilities(
            career_responsibilities,
            job_responsibilities
        )
        
        # 4. Career Match (15%)
        career_score, career_details = self._match_career(
            persona,
            job_dna
        )
        
        # 5. Title Match (10%)
        title_score = self._match_title(
            persona.get("target_titles", []),
            job_title
        )
        
        # Calculate overall weighted score
        overall_score = (
            capability_score * 0.30 +
            skill_score * 0.25 +
            responsibility_score * 0.20 +
            career_score * 0.15 +
            title_score * 0.10
        )
        
        # Determine confidence
        confidence = self._calculate_confidence(
            capability_score,
            skill_score,
            responsibility_score,
            career_score,
            title_score
        )
        
        return {
            "job_id": job.get("id"),
            "job_title": job_title,
            "company": job.get("company"),
            "location": job.get("location"),
            "overall_score": round(overall_score, 2),
            "title_match": round(title_score, 2),
            "capability_match": round(capability_score, 2),
            "skill_match": round(skill_score, 2),
            "responsibility_match": round(responsibility_score, 2),
            "career_match": round(career_score, 2),
            "capability_details": capability_details,
            "skill_details": skill_details,
            "responsibility_details": responsibility_details,
            "career_details": career_details,
            "discovery_confidence": round(confidence, 2),
            "matched_capabilities": capability_details.get("matched", []),
            "missing_capabilities": capability_details.get("missing", []),
        }
    
    def _extract_career_capabilities(self, career_profile: Dict, persona: Dict) -> List[str]:
        """Extract capabilities from career profile."""
        capabilities = []
        
        # From skills
        for skill in career_profile.get("skills", []):
            skill_name = skill.get("name", "")
            for cap, synonyms in self.capability_synonyms.items():
                if any(syn in skill_name.lower() for syn in synonyms):
                    capabilities.append(cap)
                if cap.lower() in skill_name.lower():
                    capabilities.append(cap)
        
        # From persona target titles
        for title in persona.get("target_titles", []):
            for cap, synonyms in self.capability_synonyms.items():
                if any(syn in title.lower() for syn in synonyms):
                    capabilities.append(cap)
        
        # Deduplicate
        return list(set(capabilities))
    
    def _extract_career_skills(self, career_profile: Dict, persona: Dict) -> List[str]:
        """Extract skills from career profile."""
        skills = []
        for skill in career_profile.get("skills", []):
            skills.append(skill.get("name", "").lower())
        return skills
    
    def _extract_career_responsibilities(self, career_profile: Dict) -> List[str]:
        """Extract responsibilities from career profile."""
        responsibilities = []
        for emp in career_profile.get("employments", []):
            if emp.get("responsibilities"):
                responsibilities.append(emp["responsibilities"])
        return responsibilities
    
    def _match_capabilities(self, career_caps: List[str], job_caps: Dict) -> Tuple[float, Dict]:
        """Match capabilities semantically."""
        if not job_caps:
            return 100.0, {"matched": [], "missing": [], "score": 100}
        
        job_cap_names = list(job_caps.keys())
        matched = []
        partial = []
        missing = []
        
        for job_cap in job_cap_names:
            # Check exact match
            if job_cap in career_caps:
                matched.append(job_cap)
                continue
            
            # Check semantic match
            found_match = False
            for career_cap in career_caps:
                if self._are_capabilities_related(career_cap, job_cap):
                    partial.append({"job": job_cap, "related_to": career_cap})
                    found_match = True
                    break
            
            if not found_match:
                missing.append(job_cap)
        
        # Calculate score
        if job_cap_names:
            score = (len(matched) * 1.0 + len(partial) * 0.5) / len(job_cap_names) * 100
        else:
            score = 100
        
        return min(score, 100), {
            "matched": matched,
            "partial": partial,
            "missing": missing,
            "score": min(score, 100)
        }
    
    def _match_skills(self, career_skills: List[str], job_skills: Dict) -> Tuple[float, Dict]:
        """Match skills."""
        if not job_skills:
            return 100.0, {"matched": [], "missing": [], "score": 100}
        
        job_skill_names = list(job_skills.keys())
        matched = []
        missing = []
        
        for job_skill in job_skill_names:
            if job_skill.lower() in career_skills:
                matched.append(job_skill)
            else:
                # Check for partial match
                found = False
                for career_skill in career_skills:
                    if job_skill.lower() in career_skill or career_skill in job_skill.lower():
                        matched.append(job_skill)
                        found = True
                        break
                if not found:
                    missing.append(job_skill)
        
        if job_skill_names:
            score = len(matched) / len(job_skill_names) * 100
        else:
            score = 100
        
        return min(score, 100), {
            "matched": matched,
            "missing": missing,
            "score": min(score, 100)
        }
    
    def _match_responsibilities(self, career_resp: List[str], job_resp: List[str]) -> Tuple[float, Dict]:
        """Match responsibilities."""
        if not job_resp:
            return 100.0, {"matched": [], "score": 100}
        
        if not career_resp:
            return 50.0, {"score": 50}
        
        # Simple keyword matching
        career_text = " ".join(career_resp).lower()
        matched = []
        
        for resp in job_resp:
            words = resp.lower().split()[:10]  # Take first 10 words
            matches = sum(1 for word in words if word in career_text)
            if matches > 0:
                matched.append(resp)
        
        score = len(matched) / len(job_resp) * 100 if job_resp else 100
        
        return min(score, 100), {
            "matched": matched,
            "total": len(job_resp),
            "score": min(score, 100)
        }
    
    def _match_career(self, persona: Dict, job_dna: Dict) -> Tuple[float, Dict]:
        """Match career alignment."""
        score = 0.0
        details = {}
        
        # Seniority match
        if persona.get("preferred_seniority") and job_dna.get("seniority"):
            if persona["preferred_seniority"] == job_dna["seniority"]:
                score += 30
                details["seniority"] = "match"
            else:
                score += 15
                details["seniority"] = "partial"
        
        # Industry match
        if persona.get("target_industries") and job_dna.get("industry"):
            for industry in persona["target_industries"]:
                if industry.lower() in job_dna["industry"].lower():
                    score += 20
                    details["industry"] = "match"
                    break
            else:
                score += 10
                details["industry"] = "partial"
        else:
            score += 20
        
        # Location match
        if persona.get("target_locations") and job_dna.get("location", {}).get("location"):
            for loc in persona["target_locations"]:
                if loc.lower() in job_dna["location"]["location"].lower():
                    score += 20
                    details["location"] = "match"
                    break
            else:
                score += 10
                details["location"] = "partial"
        else:
            score += 20
        
        # Remote match
        if persona.get("remote_preference") and job_dna.get("location", {}).get("remote_policy"):
            if persona["remote_preference"] == job_dna["location"]["remote_policy"]:
                score += 15
                details["remote"] = "match"
            else:
                score += 5
                details["remote"] = "partial"
        else:
            score += 15
        
        return min(score, 100), details
    
    def _match_title(self, target_titles: List[str], job_title: str) -> float:
        """Match target titles against job title."""
        if not target_titles or not job_title:
            return 50.0
        
        job_title_lower = job_title.lower()
        for title in target_titles:
            if title.lower() in job_title_lower:
                return 100.0
        
        # Check partial match
        for title in target_titles:
            words = title.lower().split()
            if any(word in job_title_lower for word in words):
                return 70.0
        
        return 30.0
    
    def _are_capabilities_related(self, cap1: str, cap2: str) -> bool:
        """Check if two capabilities are semantically related."""
        cap1_lower = cap1.lower()
        cap2_lower = cap2.lower()
        
        # Check if one contains the other
        if cap1_lower in cap2_lower or cap2_lower in cap1_lower:
            return True
        
        # Check through synonyms
        for capability, synonyms in self.capability_synonyms.items():
            cap1_in_syn = any(syn in cap1_lower for syn in synonyms)
            cap2_in_syn = any(syn in cap2_lower for syn in synonyms)
            if cap1_in_syn and cap2_in_syn:
                return True
        
        return False
    
    def _calculate_confidence(self, cap_score, skill_score, resp_score, career_score, title_score) -> float:
        """Calculate discovery confidence based on scores."""
        avg_score = (cap_score + skill_score + resp_score + career_score + title_score) / 5
        
        if avg_score >= 80:
            return 0.9
        elif avg_score >= 60:
            return 0.7
        elif avg_score >= 40:
            return 0.5
        else:
            return 0.3
