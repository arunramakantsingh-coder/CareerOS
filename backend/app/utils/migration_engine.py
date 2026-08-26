from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import re

class MigrationEngine:
    """
    Migration Intelligence Engine.
    
    Evaluates migration eligibility based on versioned immigration rules.
    Rules must be imported from verified official sources.
    """
    
    def __init__(self):
        self.disclaimer = """
        ⚠️ IMPORTANT: This is informational guidance only.
        
        Migration rules are complex and change frequently.
        This system provides AI-assisted guidance based on publicly available information.
        
        For official decisions, always consult:
        - Government immigration websites
        - Registered migration agents
        - Legal professionals
        
        Do not rely solely on this information for visa decisions.
        """
    
    def evaluate_eligibility(self, profile: Dict, country_code: str, visa_code: Optional[str] = None) -> Dict:
        """
        Evaluate migration eligibility for a user profile.
        
        Args:
            profile: User's migration profile
            country_code: Target country code
            visa_code: Specific visa code (optional)
            
        Returns:
            Eligibility evaluation with scores, requirements, and pathways
        """
        
        # Get country from database (would be injected)
        # For now, use sample data
        
        result = {
            "country": country_code,
            "visa_code": visa_code,
            "overall_eligibility": 0.0,
            "requirements_met": [],
            "requirements_partial": [],
            "requirements_not_met": [],
            "pathways": [],
            "score": 0.0,
            "recommendations": [],
            "disclaimer": self.disclaimer,
            "sources": []
        }
        
        # Check age requirements
        age_result = self._check_age_requirement(profile, country_code)
        result["requirements_met"].extend(age_result.get("met", []))
        result["requirements_partial"].extend(age_result.get("partial", []))
        result["requirements_not_met"].extend(age_result.get("not_met", []))
        
        # Check English requirements
        english_result = self._check_english_requirement(profile, country_code)
        result["requirements_met"].extend(english_result.get("met", []))
        result["requirements_partial"].extend(english_result.get("partial", []))
        result["requirements_not_met"].extend(english_result.get("not_met", []))
        
        # Check occupation requirements
        occupation_result = self._check_occupation_requirement(profile, country_code)
        result["requirements_met"].extend(occupation_result.get("met", []))
        result["requirements_partial"].extend(occupation_result.get("partial", []))
        result["requirements_not_met"].extend(occupation_result.get("not_met", []))
        
        # Check education requirements
        education_result = self._check_education_requirement(profile, country_code)
        result["requirements_met"].extend(education_result.get("met", []))
        result["requirements_partial"].extend(education_result.get("partial", []))
        result["requirements_not_met"].extend(education_result.get("not_met", []))
        
        # Check experience requirements
        experience_result = self._check_experience_requirement(profile, country_code)
        result["requirements_met"].extend(experience_result.get("met", []))
        result["requirements_partial"].extend(experience_result.get("partial", []))
        result["requirements_not_met"].extend(experience_result.get("not_met", []))
        
        # Calculate overall score
        total_requirements = len(result["requirements_met"]) + len(result["requirements_partial"]) + len(result["requirements_not_met"])
        if total_requirements > 0:
            met_score = len(result["requirements_met"]) / total_requirements * 100
            partial_score = len(result["requirements_partial"]) / total_requirements * 50
            result["score"] = (met_score + partial_score) / 100 * 100
        
        # Determine overall eligibility
        if result["score"] >= 80:
            result["overall_eligibility"] = result["score"]
            result["eligibility_status"] = "Eligible"
        elif result["score"] >= 60:
            result["overall_eligibility"] = result["score"]
            result["eligibility_status"] = "Likely Eligible"
        elif result["score"] >= 40:
            result["overall_eligibility"] = result["score"]
            result["eligibility_status"] = "Possible - Needs Improvement"
        else:
            result["overall_eligibility"] = result["score"]
            result["eligibility_status"] = "Likely Ineligible"
        
        # Generate recommendations
        result["recommendations"] = self._generate_recommendations(
            result["requirements_not_met"],
            result["requirements_partial"],
            country_code
        )
        
        # Add sample sources
        result["sources"] = self._get_sources(country_code)
        
        return result
    
    def _check_age_requirement(self, profile: Dict, country_code: str) -> Dict:
        """Check age requirements."""
        result = {"met": [], "partial": [], "not_met": []}
        
        age = profile.get("age")
        if not age:
            result["not_met"].append("Age requirement - age not provided")
            return result
        
        # Sample age requirements by country
        age_requirements = {
            "AU": {"min": 18, "max": 45, "description": "18-45 years old"},
            "NZ": {"min": 18, "max": 55, "description": "18-55 years old"},
        }
        
        req = age_requirements.get(country_code)
        if not req:
            result["partial"].append(f"Age requirement for {country_code} - check official sources")
            return result
        
        if req["min"] <= age <= req["max"]:
            result["met"].append(f"Age {age} - within {req['description']}")
        elif age < req["min"]:
            result["not_met"].append(f"Age {age} - below minimum {req['min']}")
        else:
            result["partial"].append(f"Age {age} - above maximum {req['max']} (may be eligible for other visas)")
        
        return result
    
    def _check_english_requirement(self, profile: Dict, country_code: str) -> Dict:
        """Check English language requirements."""
        result = {"met": [], "partial": [], "not_met": []}
        
        english_level = profile.get("english_level", "").lower()
        if not english_level:
            result["not_met"].append("English requirement - English level not provided")
            return result
        
        # Sample English requirements
        english_requirements = {
            "AU": {"competent": 6.0, "proficient": 7.0, "superior": 8.0},
            "NZ": {"competent": 6.0, "proficient": 7.0, "superior": 8.0},
        }
        
        req = english_requirements.get(country_code)
        if not req:
            result["partial"].append(f"English requirement for {country_code} - check official sources")
            return result
        
        english_levels = {"competent": 1, "proficient": 2, "superior": 3}
        level_score = english_levels.get(english_level, 0)
        
        if level_score >= 2:
            result["met"].append(f"English {english_level} - meets requirements")
        elif level_score >= 1:
            result["partial"].append(f"English {english_level} - may need higher score")
        else:
            result["not_met"].append(f"English {english_level} - requires Competent English")
        
        return result
    
    def _check_occupation_requirement(self, profile: Dict, country_code: str) -> Dict:
        """Check occupation requirements."""
        result = {"met": [], "partial": [], "not_met": []}
        
        occupation = profile.get("occupation_title")
        occupation_code = profile.get("occupation_code")
        
        if not occupation:
            result["not_met"].append("Occupation requirement - occupation not provided")
            return result
        
        # Sample occupation lists (would be loaded from database)
        demand_lists = {
            "AU": {
                "occupations": ["Network Architect", "Security Architect", "Cloud Engineer"],
                "codes": ["ANZSCO 262112", "ANZSCO 262113", "ANZSCO 262114"]
            },
            "NZ": {
                "occupations": ["Network Architect", "Security Architect", "Cloud Engineer"],
                "codes": ["ANZSCO 262112", "ANZSCO 262113", "ANZSCO 262114"]
            }
        }
        
        demand = demand_lists.get(country_code)
        if not demand:
            result["partial"].append(f"Occupation requirement for {country_code} - check official sources")
            return result
        
        if occupation in demand["occupations"]:
            result["met"].append(f"Occupation {occupation} - on demand list")
        elif occupation_code and occupation_code in demand["codes"]:
            result["met"].append(f"Occupation code {occupation_code} - on demand list")
        else:
            result["partial"].append(f"Occupation {occupation} - may not be on demand list, check sponsorship options")
        
        return result
    
    def _check_education_requirement(self, profile: Dict, country_code: str) -> Dict:
        """Check education requirements."""
        result = {"met": [], "partial": [], "not_met": []}
        
        education_level = profile.get("education_level", "").lower()
        if not education_level:
            result["not_met"].append("Education requirement - education not provided")
            return result
        
        # Sample education requirements
        education_requirements = {
            "AU": ["bachelors", "masters", "phd"],
            "NZ": ["bachelors", "masters", "phd"],
        }
        
        required = education_requirements.get(country_code, ["bachelors"])
        
        if any(level in education_level for level in required):
            result["met"].append(f"Education {education_level} - meets requirements")
        elif "diploma" in education_level:
            result["partial"].append(f"Education {education_level} - may need assessment")
        else:
            result["not_met"].append(f"Education {education_level} - may not meet requirements")
        
        return result
    
    def _check_experience_requirement(self, profile: Dict, country_code: str) -> Dict:
        """Check experience requirements."""
        result = {"met": [], "partial": [], "not_met": []}
        
        years_experience = profile.get("years_experience", 0)
        if years_experience == 0:
            result["not_met"].append("Experience requirement - experience not provided")
            return result
        
        # Sample experience requirements
        experience_requirements = {
            "AU": {"min": 3, "preferred": 5},
            "NZ": {"min": 3, "preferred": 5},
        }
        
        req = experience_requirements.get(country_code, {"min": 3, "preferred": 5})
        
        if years_experience >= req.get("preferred", 5):
            result["met"].append(f"Experience {years_experience} years - exceeds preferred")
        elif years_experience >= req.get("min", 3):
            result["met"].append(f"Experience {years_experience} years - meets minimum")
        else:
            result["not_met"].append(f"Experience {years_experience} years - below minimum {req['min']}")
        
        return result
    
    def _generate_recommendations(self, not_met: List[str], partial: List[str], country_code: str) -> List[str]:
        """Generate recommendations based on requirements."""
        recommendations = []
        
        for req in not_met:
            if "age" in req.lower():
                recommendations.append("Consider different visa options or waiting until eligible age")
            elif "english" in req.lower():
                recommendations.append("Take an English proficiency test (IELTS/PTE) to improve score")
            elif "occupation" in req.lower():
                recommendations.append("Check alternative occupations or employer sponsorship")
            elif "education" in req.lower():
                recommendations.append("Consider getting your qualifications assessed")
            elif "experience" in req.lower():
                recommendations.append("Gain more relevant work experience")
            else:
                recommendations.append(f"Review requirement: {req}")
        
        for req in partial:
            if "english" in req.lower():
                recommendations.append("Consider retaking English test for higher score")
            elif "occupation" in req.lower():
                recommendations.append("Research employer sponsorship options")
        
        if not recommendations:
            recommendations.append("You meet all basic requirements. Consider applying!")
        
        return recommendations
    
    def _get_sources(self, country_code: str) -> List[Dict]:
        """Get official sources for a country."""
        sources = {
            "AU": [
                {
                    "name": "Australian Department of Home Affairs",
                    "url": "https://immi.homeaffairs.gov.au/",
                    "type": "official"
                },
                {
                    "name": "Australian Skills Assessment Authorities",
                    "url": "https://www.homeaffairs.gov.au/",
                    "type": "official"
                }
            ],
            "NZ": [
                {
                    "name": "Immigration New Zealand",
                    "url": "https://www.immigration.govt.nz/",
                    "type": "official"
                },
                {
                    "name": "Skills Assessment Authority",
                    "url": "https://www.immigration.govt.nz/",
                    "type": "official"
                }
            ]
        }
        
        return sources.get(country_code, [
            {
                "name": "Official immigration website",
                "url": "Check country-specific immigration authority",
                "type": "official"
            }
        ])
    
    def get_country_info(self, country_code: str) -> Dict:
        """Get country-specific migration information."""
        country_info = {
            "AU": {
                "name": "Australia",
                "visa_types": [
                    "Skilled Independent (189)",
                    "Skilled Nominated (190)",
                    "Employer Sponsored (482)",
                    "Regional Sponsored (491)",
                    "Global Talent (858)"
                ],
                "pathways": [
                    "Points-tested skilled migration",
                    "Employer-sponsored",
                    "State/territory nominated",
                    "Regional migration",
                    "Global Talent Program"
                ],
                "key_requirements": [
                    "Age under 45",
                    "Competent English",
                    "Occupation on demand list",
                    "Skills assessment",
                    "Points test"
                ]
            },
            "NZ": {
                "name": "New Zealand",
                "visa_types": [
                    "Skilled Migrant Category (SMC)",
                    "Employer Sponsored (AEWV)",
                    "Talent (Accredited Employer)",
                    "Regional Skilled",
                    "Green List"
                ],
                "pathways": [
                    "Skilled Migrant Category",
                    "Employer-sponsored",
                    "Green List - Straight to Residence",
                    "Green List - Work to Residence",
                    "Regional migration"
                ],
                "key_requirements": [
                    "Age under 55",
                    "Competent English",
                    "Occupation on demand list",
                    "Skills assessment",
                    "Points test"
                ]
            }
        }
        
        return country_info.get(country_code, {
            "name": "Unknown",
            "visa_types": [],
            "pathways": [],
            "key_requirements": []
        })
    
    def get_disclaimer(self) -> str:
        """Get the migration disclaimer."""
        return self.disclaimer
