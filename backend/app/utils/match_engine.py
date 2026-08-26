from typing import Dict, List, Any, Optional, Tuple
import math

class MatchEngine:
    """Career-to-Job matching engine with semantic capability matching."""
    
    def __init__(self):
        # Dimension weights (configurable)
        self.dimension_weights = {
            "Technical Skills": 0.25,
            "Experience": 0.20,
            "Architecture": 0.15,
            "Responsibilities": 0.10,
            "Leadership": 0.10,
            "Industry": 0.05,
            "Seniority": 0.05,
            "Location": 0.03,
            "Remote Eligibility": 0.03,
            "Salary": 0.02,
            "Certifications": 0.02,
        }
        
        # Capability mapping for semantic matching
        self.capability_mapping = {
            "Network Architecture": ["network", "routing", "switching", "sd-wan", "lan", "wan"],
            "Security Architecture": ["security", "firewall", "ips", "ids", "zero trust", "segmentation"],
            "Cyber Security": ["cybersecurity", "cyber", "threat", "vulnerability", "incident response"],
            "Cloud Architecture": ["cloud", "aws", "azure", "gcp", "hybrid cloud"],
            "Infrastructure Architecture": ["infrastructure", "server", "storage", "virtualization"],
            "Automation": ["automation", "scripting", "ci/cd", "devops", "terraform", "ansible"],
            "IT Governance": ["governance", "it governance", "policy", "framework"],
            "Risk Management": ["risk", "risk assessment", "mitigation"],
            "Compliance": ["compliance", "regulatory", "soc2", "iso", "gdpr"],
            "Strategic Leadership": ["strategy", "vision", "roadmap", "planning", "executive"],
            "People Leadership": ["team management", "mentoring", "hiring", "performance"],
            "Digital Transformation": ["digital transformation", "modernization", "innovation"],
        }
    
    def match(self, career_profile: Dict, persona: Dict, job_dna: Dict) -> Dict:
        """
        Match a career profile + persona against a job DNA.
        
        Returns a comprehensive match result with scores and explanations.
        """
        # Calculate each dimension score
        dimension_scores = {}
        dimension_details = {}
        
        # 1. Technical Skills Match
        tech_score, tech_details = self._match_skills(
            career_profile.get("skills", {}),
            job_dna.get("skills", {}),
            persona.get("skill_weights", {})
        )
        dimension_scores["Technical Skills"] = tech_score
        dimension_details["Technical Skills"] = tech_details
        
        # 2. Experience Match
        exp_score, exp_details = self._match_experience(
            career_profile.get("employments", []),
            job_dna.get("experience_requirements", {})
        )
        dimension_scores["Experience"] = exp_score
        dimension_details["Experience"] = exp_details
        
        # 3. Architecture Match
        arch_score, arch_details = self._match_architecture(
            career_profile.get("technologies", []),
            job_dna.get("architecture_domains", [])
        )
        dimension_scores["Architecture"] = arch_score
        dimension_details["Architecture"] = arch_details
        
        # 4. Responsibilities Match
        resp_score, resp_details = self._match_responsibilities(
            career_profile.get("employments", []),
            job_dna.get("responsibilities", [])
        )
        dimension_scores["Responsibilities"] = resp_score
        dimension_details["Responsibilities"] = resp_details
        
        # 5. Leadership Match
        lead_score, lead_details = self._match_leadership(
            career_profile.get("leadership", {}),
            job_dna.get("leadership_scope", {})
        )
        dimension_scores["Leadership"] = lead_score
        dimension_details["Leadership"] = lead_details
        
        # 6. Industry Match
        ind_score, ind_details = self._match_industry(
            career_profile.get("industries", []),
            job_dna.get("industry")
        )
        dimension_scores["Industry"] = ind_score
        dimension_details["Industry"] = ind_details
        
        # 7. Seniority Match
        sen_score, sen_details = self._match_seniority(
            career_profile.get("seniority"),
            career_profile.get("years_experience"),
            job_dna.get("seniority"),
            job_dna.get("experience_requirements", {})
        )
        dimension_scores["Seniority"] = sen_score
        dimension_details["Seniority"] = sen_details
        
        # 8. Location Match
        loc_score, loc_details = self._match_location(
            persona.get("target_locations", []),
            job_dna.get("location", {})
        )
        dimension_scores["Location"] = loc_score
        dimension_details["Location"] = loc_details
        
        # 9. Remote Eligibility
        rem_score, rem_details = self._match_remote(
            persona.get("remote_preference"),
            job_dna.get("location", {}).get("remote_policy")
        )
        dimension_scores["Remote Eligibility"] = rem_score
        dimension_details["Remote Eligibility"] = rem_details
        
        # 10. Salary Match
        sal_score, sal_details = self._match_salary(
            persona.get("salary_preferences", {}),
            job_dna.get("salary", {})
        )
        dimension_scores["Salary"] = sal_score
        dimension_details["Salary"] = sal_details
        
        # 11. Certifications Match
        cert_score, cert_details = self._match_certifications(
            career_profile.get("certifications", []),
            job_dna.get("certifications_required", {})
        )
        dimension_scores["Certifications"] = cert_score
        dimension_details["Certifications"] = cert_details
        
        # Calculate overall weighted score
        overall_score = self._calculate_overall_score(dimension_scores)
        
        # Determine status
        status = self._determine_status(overall_score, dimension_scores)
        
        # Generate gaps and risks
        gaps = self._identify_gaps(dimension_details)
        risks = self._identify_risks(gaps)
        
        # Generate summary and recommendation
        summary = self._generate_summary(overall_score, status, dimension_scores)
        recommendation = self._generate_recommendation(gaps, risks)
        
        # Compile matched/partial/missing skills
        matched_skills = dimension_details.get("Technical Skills", {}).get("matched", [])
        partial_skills = dimension_details.get("Technical Skills", {}).get("partial", [])
        missing_skills = dimension_details.get("Technical Skills", {}).get("missing", [])
        
        return {
            "overall_score": overall_score,
            "dimension_scores": dimension_scores,
            "dimension_details": dimension_details,
            "status": status,
            "summary": summary,
            "recommendation": recommendation,
            "matched_skills": matched_skills,
            "partial_skills": partial_skills,
            "missing_skills": missing_skills,
            "hard_failures": [],
            "gaps": gaps,
            "risks": risks,
        }
    
    def _match_skills(self, user_skills: Dict, job_skills: Dict, skill_weights: Dict) -> Tuple[float, Dict]:
        """Match skills with semantic capability matching."""
        matched = []
        partial = []
        missing = []
        
        user_skill_names = set(user_skills.keys())
        job_skill_names = set(job_skills.keys())
        
        # Find exact matches
        exact_matches = user_skill_names.intersection(job_skill_names)
        for skill in exact_matches:
            matched.append({"skill": skill, "match_type": "exact"})
        
        # Find semantic matches using capability mapping
        for skill in job_skill_names:
            if skill in user_skill_names:
                continue  # Already matched
            
            # Check if user has any semantically related skill
            found_match = False
            for user_skill in user_skill_names:
                if self._are_skills_semantically_related(user_skill, skill):
                    matched.append({"skill": skill, "match_type": "semantic", "related_to": user_skill})
                    found_match = True
                    break
            
            if not found_match:
                missing.append(skill)
        
        # Calculate score
        if job_skill_names:
            matched_count = len([m for m in matched if m.get("match_type") == "exact"])
            semantic_count = len([m for m in matched if m.get("match_type") == "semantic"])
            
            # Weight exact matches higher
            score = (matched_count * 1.0 + semantic_count * 0.7) / len(job_skill_names) * 100
        else:
            score = 100.0  # No skills required
        
        return min(score, 100), {
            "matched": matched,
            "partial": partial,
            "missing": missing,
            "score": min(score, 100)
        }
    
    def _are_skills_semantically_related(self, skill1: str, skill2: str) -> bool:
        """Check if two skills are semantically related using capability mapping."""
        skill1_lower = skill1.lower()
        skill2_lower = skill2.lower()
        
        # Check direct word overlap
        words1 = set(skill1_lower.split())
        words2 = set(skill2_lower.split())
        if len(words1.intersection(words2)) > 0:
            return True
        
        # Check through capability mapping
        for capability, keywords in self.capability_mapping.items():
            skill1_in_cap = any(kw in skill1_lower for kw in keywords)
            skill2_in_cap = any(kw in skill2_lower for kw in keywords)
            if skill1_in_cap and skill2_in_cap:
                return True
        
        return False
    
    def _match_experience(self, employments: List, requirements: Dict) -> Tuple[float, Dict]:
        """Match experience years and fields."""
        years = sum([
            self._calculate_years(e.get("start_date"), e.get("end_date"))
            for e in employments
            if e.get("start_date")
        ])
        
        required_years = requirements.get("minimum", 0)
        
        if years >= required_years:
            score = 100
        elif years >= required_years * 0.7:
            score = 70
        elif years >= required_years * 0.5:
            score = 50
        else:
            score = 30
        
        return min(score, 100), {
            "years": years,
            "required": required_years,
            "score": min(score, 100)
        }
    
    def _match_architecture(self, technologies: List, domains: List) -> Tuple[float, Dict]:
        """Match architecture domains."""
        if not domains:
            return 100, {"score": 100}
        
        tech_names = [t.get("name", "").lower() for t in technologies]
        matched = []
        
        for domain in domains:
            domain_lower = domain.lower()
            # Check if any technology matches the domain
            for tech in tech_names:
                if domain_lower in tech or tech in domain_lower:
                    matched.append(domain)
                    break
        
        score = (len(matched) / len(domains)) * 100 if domains else 100
        
        return min(score, 100), {
            "matched": matched,
            "total": len(domains),
            "score": min(score, 100)
        }
    
    def _match_leadership(self, user_leadership: Dict, job_leadership: Dict) -> Tuple[float, Dict]:
        """Match leadership scope."""
        if not job_leadership:
            return 100, {"score": 100}
        
        job_people = job_leadership.get("people", 0)
        job_budget = job_leadership.get("budget", 0)
        job_strategic = job_leadership.get("strategic", False)
        
        user_people = user_leadership.get("people", 0)
        user_budget = user_leadership.get("budget", 0)
        user_strategic = user_leadership.get("strategic", False)
        
        # Calculate match
        people_match = min(user_people / job_people, 1) if job_people > 0 else 1
        budget_match = min(user_budget / job_budget, 1) if job_budget > 0 else 1
        strategic_match = 1 if user_strategic == job_strategic else 0.5
        
        score = ((people_match * 0.4) + (budget_match * 0.3) + (strategic_match * 0.3)) * 100
        
        return min(score, 100), {
            "people": people_match,
            "budget": budget_match,
            "strategic": strategic_match,
            "score": min(score, 100)
        }
    
    def _match_industry(self, user_industries: List, job_industry: str) -> Tuple[float, Dict]:
        """Match industry experience."""
        if not job_industry:
            return 100, {"score": 100}
        
        if not user_industries:
            return 50, {"score": 50}
        
        # Check if any user industry matches job industry
        job_lower = job_industry.lower()
        for industry in user_industries:
            if job_lower in industry.lower() or industry.lower() in job_lower:
                return 100, {"score": 100}
        
        return 50, {"score": 50}
    
    def _match_seniority(self, user_seniority: str, years: int, job_seniority: str, requirements: Dict) -> Tuple[float, Dict]:
        """Match seniority level."""
        seniority_levels = ["entry", "mid", "senior", "lead", "manager", "director", "executive"]
        job_level_index = seniority_levels.index(job_seniority) if job_seniority in seniority_levels else -1
        user_level_index = seniority_levels.index(user_seniority) if user_seniority in seniority_levels else -1
        
        if job_level_index == -1:
            return 100, {"score": 100}
        
        if user_level_index >= job_level_index:
            score = 100
        elif user_level_index == job_level_index - 1:
            score = 70
        elif user_level_index == job_level_index - 2:
            score = 50
        else:
            score = 30
        
        return min(score, 100), {
            "user_seniority": user_seniority,
            "job_seniority": job_seniority,
            "score": min(score, 100)
        }
    
    def _match_location(self, target_locations: List, job_location: Dict) -> Tuple[float, Dict]:
        """Match location preferences."""
        if not target_locations or not job_location:
            return 100, {"score": 100}
        
        job_loc = job_location.get("location", "").lower()
        for loc in target_locations:
            if loc.lower() in job_loc:
                return 100, {"score": 100}
        
        return 50, {"score": 50}
    
    def _match_remote(self, user_remote_pref: str, job_remote_policy: str) -> Tuple[float, Dict]:
        """Match remote eligibility."""
        if not job_remote_policy:
            return 100, {"score": 100}
        
        if not user_remote_pref:
            return 50, {"score": 50}
        
        # Remote preference mapping
        remote_mapping = {
            "Remote": ["Remote", "Hybrid"],
            "Hybrid": ["Hybrid", "Remote", "On-site"],
            "On-site": ["On-site", "Hybrid"],
            "Any": ["Remote", "Hybrid", "On-site"],
        }
        
        if job_remote_policy in remote_mapping.get(user_remote_pref, []):
            return 100, {"score": 100}
        else:
            return 50, {"score": 50}
    
    def _match_salary(self, user_salary: Dict, job_salary: Dict) -> Tuple[float, Dict]:
        """Match salary expectations."""
        if not job_salary or not user_salary:
            return 100, {"score": 100}
        
        user_min = user_salary.get("min", 0)
        user_max = user_salary.get("max", float('inf'))
        job_min = job_salary.get("min", 0)
        job_max = job_salary.get("max", float('inf'))
        
        # Check if salary ranges overlap
        if user_max >= job_min and user_min <= job_max:
            return 100, {"score": 100}
        elif user_max >= job_min * 0.8:
            return 70, {"score": 70}
        else:
            return 50, {"score": 50}
    
    def _match_certifications(self, user_certs: List, job_certs: Dict) -> Tuple[float, Dict]:
        """Match certifications."""
        if not job_certs:
            return 100, {"score": 100}
        
        cert_names = [c.get("name", "").lower() for c in user_certs]
        job_cert_names = list(job_certs.keys())
        
        matched = []
        for cert in job_cert_names:
            if cert.lower() in cert_names:
                matched.append(cert)
        
        score = (len(matched) / len(job_cert_names)) * 100 if job_cert_names else 100
        
        return min(score, 100), {
            "matched": matched,
            "total": len(job_cert_names),
            "score": min(score, 100)
        }
    
    def _calculate_overall_score(self, dimension_scores: Dict) -> float:
        """Calculate weighted overall score."""
        total_score = 0
        total_weight = 0
        
        for dimension, score in dimension_scores.items():
            weight = self.dimension_weights.get(dimension, 0.1)
            total_score += score * weight
            total_weight += weight
        
        return round(total_score / total_weight, 2) if total_weight > 0 else 0
    
    def _determine_status(self, overall_score: float, dimension_scores: Dict) -> str:
        """Determine match status."""
        # Check for any dimension below 40 (hard failure)
        for dimension, score in dimension_scores.items():
            if score < 40 and dimension in ["Technical Skills", "Experience", "Architecture"]:
                return "MISSING"
        
        if overall_score >= 80:
            return "MATCHED"
        elif overall_score >= 60:
            return "PARTIAL"
        elif overall_score >= 40:
            return "RISK"
        else:
            return "MISSING"
    
    def _identify_gaps(self, dimension_details: Dict) -> Dict:
        """Identify gaps from dimension details."""
        gaps = {}
        
        for dimension, details in dimension_details.items():
            missing = details.get("missing", [])
            if missing:
                gaps[dimension] = missing
        
        return gaps
    
    def _identify_risks(self, gaps: Dict) -> List:
        """Identify risks based on gaps."""
        risks = []
        for dimension, items in gaps.items():
            if dimension == "Technical Skills":
                risks.append(f"Missing required technical skills: {', '.join(items[:3])}")
            elif dimension == "Certifications":
                risks.append(f"Missing required certifications: {', '.join(items[:3])}")
            elif dimension == "Experience":
                risks.append("Experience requirements may not be fully met")
        return risks
    
    def _generate_summary(self, overall_score: float, status: str, dimension_scores: Dict) -> str:
        """Generate a summary of the match."""
        top_dimensions = sorted(dimension_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        bottom_dimensions = sorted(dimension_scores.items(), key=lambda x: x[1])[:3]
        
        summary = f"Overall match score: {overall_score:.1f}% - Status: {status}. "
        summary += f"Strongest dimensions: {', '.join([f'{d}({s:.0f}%)' for d, s in top_dimensions])}. "
        summary += f"Areas to improve: {', '.join([f'{d}({s:.0f}%)' for d, s in bottom_dimensions])}."
        
        return summary
    
    def _generate_recommendation(self, gaps: Dict, risks: List) -> str:
        """Generate recommendations based on gaps and risks."""
        recommendations = []
        
        if gaps.get("Technical Skills"):
            skills = gaps["Technical Skills"][:3]
            recommendations.append(f"Consider developing these skills: {', '.join(skills)}")
        
        if gaps.get("Certifications"):
            certs = gaps["Certifications"][:3]
            recommendations.append(f"Consider obtaining: {', '.join(certs)}")
        
        if "Experience" in gaps:
            recommendations.append("Gain more experience in this domain")
        
        if not recommendations:
            recommendations.append("You are well-aligned with this role. Consider applying!")
        
        return " ".join(recommendations)
    
    def _calculate_years(self, start_date: Any, end_date: Any) -> float:
        """Calculate years between two dates."""
        if not start_date:
            return 0
        
        from datetime import datetime
        if isinstance(start_date, datetime):
            start = start_date
            end = end_date or datetime.now()
            return (end - start).days / 365.25
        
        return 0
