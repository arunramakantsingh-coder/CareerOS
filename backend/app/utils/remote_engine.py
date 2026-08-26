from typing import Dict, List, Any, Optional, Tuple
import re
from datetime import datetime

class RemoteEngine:
    """
    Remote Eligibility Intelligence Engine.
    
    Evaluates remote eligibility based on:
    - Candidate location
    - Timezone compatibility
    - Work authorization
    - Contractor/EOR possibilities
    - Relocation requirements
    - Sponsorship requirements
    """
    
    # Timezone offset mapping (UTC)
    TIMEZONE_OFFSETS = {
        "UTC": 0,
        "GMT": 0,
        "EST": -5,
        "EDT": -4,
        "CST": -6,
        "CDT": -5,
        "MST": -7,
        "MDT": -6,
        "PST": -8,
        "PDT": -7,
        "CET": 1,
        "CEST": 2,
        "EET": 2,
        "EEST": 3,
        "IST": 5.5,
        "SGT": 8,
        "AEST": 10,
        "AEDT": 11,
        "JST": 9,
        "NZST": 12,
        "NZDT": 13,
        "BRT": -3,
        "ART": -3,
        "PKT": 5,
        "GST": 4,
        "MSK": 3,
    }
    
    # Country to region mapping
    COUNTRY_REGIONS = {
        "US": "US",
        "USA": "US",
        "United States": "US",
        "UK": "UK",
        "United Kingdom": "UK",
        "GB": "UK",
        "India": "India",
        "EU": "EU",
        "Germany": "EU",
        "France": "EU",
        "Italy": "EU",
        "Spain": "EU",
        "Netherlands": "EU",
        "Sweden": "EU",
        "Denmark": "EU",
        "Austria": "EU",
        "Switzerland": "EU",
        "Belgium": "EU",
        "Ireland": "EU",
        "Portugal": "EU",
        "Finland": "EU",
        "Norway": "EU",
        "Poland": "EU",
        "Romania": "EU",
    }
    
    def __init__(self):
        self.country_regions = self.COUNTRY_REGIONS
    
    def evaluate(self, user: Dict, job: Dict) -> Dict:
        """
        Evaluate remote eligibility for a user-job pair.
        
        Args:
            user: User data with location, timezone, authorization
            job: Job data with location, remote_policy, job_dna
            
        Returns:
            Remote eligibility evaluation with scores and flags
        """
        
        # 1. Classify the job
        classification = self._classify_job(job)
        
        # 2. Check timezone compatibility
        timezone_score, is_timezone_compatible = self._check_timezone(
            user.get("candidate_timezone", "UTC"),
            job
        )
        
        # 3. Check work authorization
        auth_score, has_auth = self._check_authorization(
            user.get("candidate_authorization", {}),
            job
        )
        
        # 4. Check sponsorship
        sponsorship_score, requires_sponsorship = self._check_sponsorship(
            user.get("candidate_authorization", {}),
            job
        )
        
        # 5. Check contractor/EOR possibilities
        contractor_score, allows_contractor, allows_eor = self._check_contractor(job)
        
        # 6. Check relocation requirement
        relocation_score, requires_relocation = self._check_relocation(job)
        
        # 7. Calculate overall score
        overall_score = self._calculate_overall_score(
            timezone_score,
            auth_score,
            sponsorship_score,
            contractor_score,
            relocation_score,
            classification
        )
        
        # 8. Determine eligibility
        is_eligible = self._determine_eligibility(
            overall_score,
            is_timezone_compatible,
            has_auth,
            requires_sponsorship,
            requires_relocation
        )
        
        # 9. Extract restrictions and requirements
        restrictions = self._extract_restrictions(job, classification)
        requirements = self._extract_requirements(job, user)
        
        return {
            "remote_classification": classification,
            "overall_remote_score": round(overall_score, 2),
            "timezone_score": round(timezone_score, 2),
            "authorization_score": round(auth_score, 2),
            "sponsorship_score": round(sponsorship_score, 2),
            "contractor_score": round(contractor_score, 2),
            "relocation_score": round(relocation_score, 2),
            "is_remote_eligible": is_eligible,
            "is_timezone_compatible": is_timezone_compatible,
            "has_work_authorization": has_auth,
            "requires_sponsorship": requires_sponsorship,
            "requires_relocation": requires_relocation,
            "allows_contractor": allows_contractor,
            "allows_eor": allows_eor,
            "restrictions": restrictions,
            "requirements": requirements,
            "remote_analysis": self._generate_analysis(
                classification,
                overall_score,
                restrictions,
                is_eligible
            )
        }
    
    def _classify_job(self, job: Dict) -> str:
        """Classify job remote scope."""
        location = job.get("location", "")
        remote_policy = job.get("remote_policy", "").lower()
        
        # Get job_dna for additional context
        job_dna = job.get("job_dna", {})
        location_info = job_dna.get("location", {})
        mobility = job_dna.get("mobility_requirements", {})
        
        # Check remote policy first
        if "worldwide" in remote_policy or "global" in remote_policy:
            return "worldwide"
        
        if "remote" in remote_policy:
            # Need to determine scope from location or description
            location_lower = location.lower()
            
            if "us" in location_lower or "usa" in location_lower or "united states" in location_lower:
                if "only" in remote_policy or "exclusively" in remote_policy:
                    return "us-only"
                return "us-only"
            
            if "uk" in location_lower or "united kingdom" in location_lower or "gb" in location_lower:
                if "only" in remote_policy or "exclusively" in remote_policy:
                    return "uk-only"
                return "uk-only"
            
            if "eu" in location_lower or "europe" in location_lower:
                return "eu-only"
            
            if "india" in location_lower:
                return "india-only"
            
            # Check mobility requirements
            if mobility.get("sponsorship") or mobility.get("relocation"):
                return "country-specific"
            
            # Check location info
            if location_info.get("country"):
                country = location_info["country"].lower()
                if country in ["us", "usa", "united states"]:
                    return "us-only"
                if country in ["uk", "united kingdom"]:
                    return "uk-only"
                if country == "india":
                    return "india-only"
                # Check if in EU
                for eu_country in ["germany", "france", "italy", "spain", "netherlands", "sweden", 
                                  "denmark", "austria", "switzerland", "belgium", "ireland"]:
                    if eu_country in country:
                        return "eu-only"
                return "country-specific"
            
            return "region-specific"
        
        return "unknown"
    
    def _check_timezone(self, candidate_timezone: str, job: Dict) -> Tuple[float, bool]:
        """Check timezone compatibility."""
        if not candidate_timezone:
            return 50.0, False
        
        candidate_offset = self.TIMEZONE_OFFSETS.get(candidate_timezone.upper(), 0)
        
        # Get job timezone from location or job_dna
        job_timezone = "UTC"  # Default
        job_dna = job.get("job_dna", {})
        location_info = job_dna.get("location", {})
        
        if location_info.get("timezone"):
            job_timezone = location_info["timezone"]
        
        job_offset = self.TIMEZONE_OFFSETS.get(job_timezone.upper(), 0)
        
        # Calculate offset difference
        diff = abs(candidate_offset - job_offset)
        
        # Score based on timezone difference
        if diff <= 1:
            return 100.0, True
        elif diff <= 2:
            return 80.0, True
        elif diff <= 3:
            return 60.0, True
        elif diff <= 4:
            return 40.0, False
        else:
            return 20.0, False
    
    def _check_authorization(self, auth: Dict, job: Dict) -> Tuple[float, bool]:
        """Check work authorization."""
        if not auth:
            return 50.0, False
        
        authorized_countries = auth.get("countries", [])
        if not authorized_countries:
            return 50.0, False
        
        # Check if job location is in authorized countries
        job_dna = job.get("job_dna", {})
        location_info = job_dna.get("location", {})
        job_country = location_info.get("country", "")
        
        if job_country:
            for country in authorized_countries:
                if country.upper() in job_country.upper() or job_country.upper() in country.upper():
                    return 100.0, True
            return 30.0, False
        
        # If no specific country, check region
        job_location = job.get("location", "")
        for country in authorized_countries:
            if country.upper() in job_location.upper():
                return 100.0, True
        
        return 50.0, False
    
    def _check_sponsorship(self, auth: Dict, job: Dict) -> Tuple[float, bool]:
        """Check sponsorship requirements."""
        job_dna = job.get("job_dna", {})
        mobility = job_dna.get("mobility_requirements", {})
        
        if mobility.get("sponsorship") or mobility.get("visa_required"):
            # Check if candidate has authorization
            authorized_countries = auth.get("countries", [])
            job_dna = job.get("job_dna", {})
            location_info = job_dna.get("location", {})
            job_country = location_info.get("country", "")
            
            if job_country:
                for country in authorized_countries:
                    if country.upper() in job_country.upper() or job_country.upper() in country.upper():
                        return 100.0, False
                return 0.0, True
            
            return 50.0, True
        
        return 100.0, False
    
    def _check_contractor(self, job: Dict) -> Tuple[float, bool, bool]:
        """Check contractor/EOR possibilities."""
        job_dna = job.get("job_dna", {})
        employment_model = job_dna.get("employment_model", {})
        mobility = job_dna.get("mobility_requirements", {})
        
        allows_contractor = True
        allows_eor = True
        
        # Check if employment model mentions contractor
        if employment_model:
            if "employee" in employment_model.lower():
                allows_contractor = False
            if "contractor" in employment_model.lower() or "freelance" in employment_model.lower():
                allows_contractor = True
        
        # Check mobility
        if mobility.get("sponsorship"):
            allows_contractor = True  # Contractor might be easier
            allows_eor = True
        
        score = 100.0 if (allows_contractor or allows_eor) else 50.0
        
        return score, allows_contractor, allows_eor
    
    def _check_relocation(self, job: Dict) -> Tuple[float, bool]:
        """Check relocation requirements."""
        job_dna = job.get("job_dna", {})
        mobility = job_dna.get("mobility_requirements", {})
        
        if mobility.get("relocation"):
            return 0.0, True
        else:
            return 100.0, False
    
    def _calculate_overall_score(self, timezone_score, auth_score, sponsorship_score, 
                                 contractor_score, relocation_score, classification) -> float:
        """Calculate overall remote score."""
        # Weights
        weights = {
            "timezone": 0.25,
            "authorization": 0.25,
            "sponsorship": 0.20,
            "contractor": 0.15,
            "relocation": 0.15
        }
        
        overall = (
            timezone_score * weights["timezone"] +
            auth_score * weights["authorization"] +
            sponsorship_score * weights["sponsorship"] +
            contractor_score * weights["contractor"] +
            relocation_score * weights["relocation"]
        )
        
        # Adjust for classification
        if classification in ["worldwide", "remote"]:
            overall = min(overall * 1.1, 100)
        elif classification in ["us-only", "uk-only", "eu-only", "india-only"]:
            overall = overall * 0.9
        
        return min(overall, 100)
    
    def _determine_eligibility(self, overall_score, is_timezone_compatible, 
                              has_auth, requires_sponsorship, requires_relocation) -> bool:
        """Determine if remote eligible."""
        if requires_sponsorship:
            return False
        if requires_relocation:
            return False
        if not has_auth:
            return False
        if not is_timezone_compatible:
            return False
        if overall_score < 50:
            return False
        
        return True
    
    def _extract_restrictions(self, job: Dict, classification: str) -> List[str]:
        """Extract remote restrictions from job."""
        restrictions = []
        job_dna = job.get("job_dna", {})
        mobility = job_dna.get("mobility_requirements", {})
        
        # Classification-based restrictions
        if classification == "us-only":
            restrictions.append("US citizens/permanent residents only")
        elif classification == "uk-only":
            restrictions.append("UK residents only")
        elif classification == "eu-only":
            restrictions.append("EU residents only")
        elif classification == "india-only":
            restrictions.append("India residents only")
        elif classification == "country-specific" and job.get("location"):
            restrictions.append(f"Must be in {job['location']}")
        
        # Mobility-based restrictions
        if mobility.get("sponsorship"):
            restrictions.append("Visa sponsorship not available")
        if mobility.get("relocation"):
            restrictions.append("Relocation required")
        
        # Employment model restrictions
        employment_model = job_dna.get("employment_model", {})
        if employment_model.get("type") == "employee":
            restrictions.append("Must be a W-2 employee")
        
        return restrictions
    
    def _extract_requirements(self, job: Dict, user: Dict) -> List[str]:
        """Extract remote requirements."""
        requirements = []
        job_dna = job.get("job_dna", {})
        
        # Timezone requirement
        if job_dna.get("location", {}).get("timezone"):
            tz = job_dna["location"]["timezone"]
            requirements.append(f"Must work {tz} timezone hours")
        
        # Work hours overlap
        if "hybrid" in str(job.get("remote_policy", "")).lower():
            requirements.append("Requires some in-office days")
        
        # Equipment requirements
        if job_dna.get("technologies"):
            techs = job_dna["technologies"][:3]
            requirements.append(f"Requires experience with: {', '.join(techs)}")
        
        return requirements
    
    def _generate_analysis(self, classification: str, overall_score: float,
                           restrictions: List[str], is_eligible: bool) -> str:
        """Generate human-readable analysis."""
        analysis = f"Remote classification: {classification.upper()}. "
        
        if is_eligible:
            analysis += "✅ Candidate is eligible for remote work. "
        else:
            analysis += "⚠️ Candidate may not be eligible for remote work. "
        
        if restrictions:
            analysis += f"Restrictions: {'; '.join(restrictions)}. "
        
        analysis += f"Overall remote score: {overall_score:.0f}%."
        
        return analysis
