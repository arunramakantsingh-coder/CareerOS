"""Seed migration data for Australia and New Zealand."""

COUNTRIES = [
    {
        "code": "AU",
        "name": "Australia",
        "region": "Oceania",
        "immigration_authority": "Australian Department of Home Affairs",
        "official_website": "https://immi.homeaffairs.gov.au/",
        "description": "Australia offers various skilled migration pathways for professionals."
    },
    {
        "code": "NZ",
        "name": "New Zealand",
        "region": "Oceania",
        "immigration_authority": "Immigration New Zealand",
        "official_website": "https://www.immigration.govt.nz/",
        "description": "New Zealand offers skilled migration pathways through the Skilled Migrant Category."
    }
]

VISAS_AU = [
    {"code": "189", "name": "Skilled Independent Visa", "category": "Skilled"},
    {"code": "190", "name": "Skilled Nominated Visa", "category": "Skilled"},
    {"code": "482", "name": "Temporary Skill Shortage Visa", "category": "Employer-Sponsored"},
    {"code": "491", "name": "Skilled Regional Visa", "category": "Regional"},
    {"code": "858", "name": "Global Talent Visa", "category": "Talent"},
]

VISAS_NZ = [
    {"code": "SMC", "name": "Skilled Migrant Category", "category": "Skilled"},
    {"code": "AEWV", "name": "Accredited Employer Work Visa", "category": "Employer-Sponsored"},
    {"code": "SIR", "name": "Straight to Residence (Green List)", "category": "Green List"},
    {"code": "WTR", "name": "Work to Residence (Green List)", "category": "Green List"},
]

RULES_AU = [
    {
        "visa_code": "189",
        "rule_key": "age",
        "rule_type": "requirement",
        "rule_value": {"min": 18, "max": 45},
        "description": "Age requirement for Skilled Independent Visa",
        "condition_text": "Must be between 18 and 45 years old at time of application",
        "source_type": "legislation",
        "source_url": "https://immi.homeaffairs.gov.au/"
    },
    {
        "visa_code": "189",
        "rule_key": "english",
        "rule_type": "requirement",
        "rule_value": {"level": "Competent", "test": "IELTS", "score": 6.0},
        "description": "English language requirement",
        "condition_text": "Competent English (IELTS 6.0 in each band)",
        "source_type": "policy",
        "source_url": "https://immi.homeaffairs.gov.au/"
    },
    {
        "visa_code": "189",
        "rule_key": "occupation",
        "rule_type": "requirement",
        "rule_value": {"list": "MLTSSL", "status": "required"},
        "description": "Occupation must be on the Medium and Long-term Strategic Skills List",
        "condition_text": "Occupation must be on the MLTSSL",
        "source_type": "policy",
        "source_url": "https://immi.homeaffairs.gov.au/"
    },
    {
        "visa_code": "189",
        "rule_key": "points",
        "rule_type": "condition",
        "rule_value": {"minimum": 65},
        "description": "Minimum points required",
        "condition_text": "Must score at least 65 points in the points test",
        "source_type": "policy",
        "source_url": "https://immi.homeaffairs.gov.au/"
    }
]

RULES_NZ = [
    {
        "visa_code": "SMC",
        "rule_key": "age",
        "rule_type": "requirement",
        "rule_value": {"min": 18, "max": 55},
        "description": "Age requirement for Skilled Migrant Category",
        "condition_text": "Must be between 18 and 55 years old",
        "source_type": "legislation",
        "source_url": "https://www.immigration.govt.nz/"
    },
    {
        "visa_code": "SMC",
        "rule_key": "english",
        "rule_type": "requirement",
        "rule_value": {"level": "Competent", "test": "IELTS", "score": 6.0},
        "description": "English language requirement",
        "condition_text": "Competent English (IELTS 6.0 in each band)",
        "source_type": "policy",
        "source_url": "https://www.immigration.govt.nz/"
    },
    {
        "visa_code": "SMC",
        "rule_key": "occupation",
        "rule_type": "requirement",
        "rule_value": {"list": "ANZSCO", "levels": [1, 2, 3]},
        "description": "Occupation must be on the ANZSCO list at skill levels 1-3",
        "condition_text": "Occupation must be on ANZSCO skill levels 1, 2, or 3",
        "source_type": "policy",
        "source_url": "https://www.immigration.govt.nz/"
    },
    {
        "visa_code": "SMC",
        "rule_key": "points",
        "rule_type": "condition",
        "rule_value": {"minimum": 100},
        "description": "Minimum points required",
        "condition_text": "Must score at least 100 points in the points test (180 for selection)",
        "source_type": "policy",
        "source_url": "https://www.immigration.govt.nz/"
    }
]

OCCUPATIONS = [
    {"country_code": "AU", "anzsc_code": "262112", "title": "Network Architect", "skill_level": 1},
    {"country_code": "AU", "anzsc_code": "262113", "title": "Security Architect", "skill_level": 1},
    {"country_code": "AU", "anzsc_code": "262114", "title": "Cloud Engineer", "skill_level": 1},
    {"country_code": "NZ", "anzsc_code": "262112", "title": "Network Architect", "skill_level": 1},
    {"country_code": "NZ", "anzsc_code": "262113", "title": "Security Architect", "skill_level": 1},
    {"country_code": "NZ", "anzsc_code": "262114", "title": "Cloud Engineer", "skill_level": 1},
]

PATHWAYS_AU = [
    {
        "visa_code": "189",
        "name": "Points-Tested Skilled Migration",
        "pathway_type": "skilled",
        "requirements": {"points": 65, "occupation": "MLTSSL", "age": {"min": 18, "max": 45}},
        "points_required": 65
    },
    {
        "visa_code": "190",
        "name": "State Nominated Skilled Migration",
        "pathway_type": "skilled",
        "requirements": {"points": 65, "occupation": "STSOL", "age": {"min": 18, "max": 45}},
        "points_required": 65
    },
    {
        "visa_code": "482",
        "name": "Employer Sponsored",
        "pathway_type": "employer-sponsored",
        "requirements": {"occupation": "MLTSSL or STSOL", "experience": 2},
        "points_required": None
    }
]

PATHWAYS_NZ = [
    {
        "visa_code": "SMC",
        "name": "Skilled Migrant Category",
        "pathway_type": "skilled",
        "requirements": {"points": 100, "occupation": "ANZSCO", "age": {"min": 18, "max": 55}},
        "points_required": 100
    },
    {
        "visa_code": "AEWV",
        "name": "Accredited Employer Work Visa",
        "pathway_type": "employer-sponsored",
        "requirements": {"occupation": "ANZSCO", "experience": 2},
        "points_required": None
    },
    {
        "visa_code": "SIR",
        "name": "Green List - Straight to Residence",
        "pathway_type": "green-list",
        "requirements": {"occupation": "Green List", "experience": 0},
        "points_required": None
    }
]

def seed_migration_data(db):
    """Seed migration data into database."""
    from app.models.country import Country
    from app.models.visa import Visa
    from app.models.migration_rule import MigrationRule
    from app.models.occupation_mapping import OccupationMapping
    from app.models.migration_pathway import MigrationPathway
    from datetime import datetime
    
    # Seed countries
    country_map = {}
    for country_data in COUNTRIES:
        country = Country(**country_data)
        db.add(country)
        db.flush()
        country_map[country_data["code"]] = country
    
    # Seed visas
    visa_map = {}
    for visa_data in VISAS_AU:
        visa = Visa(
            country_id=country_map["AU"].id,
            **visa_data
        )
        db.add(visa)
        db.flush()
        visa_map[f"AU_{visa_data['code']}"] = visa
    
    for visa_data in VISAS_NZ:
        visa = Visa(
            country_id=country_map["NZ"].id,
            **visa_data
        )
        db.add(visa)
        db.flush()
        visa_map[f"NZ_{visa_data['code']}"] = visa
    
    # Seed rules
    for rule_data in RULES_AU:
        visa_key = f"AU_{rule_data['visa_code']}"
        if visa_key in visa_map:
            rule = MigrationRule(
                visa_id=visa_map[visa_key].id,
                effective_from=datetime.now(),
                verified_at=datetime.now(),
                verified_by="system",
                **{k: v for k, v in rule_data.items() if k != 'visa_code'}
            )
            db.add(rule)
    
    for rule_data in RULES_NZ:
        visa_key = f"NZ_{rule_data['visa_code']}"
        if visa_key in visa_map:
            rule = MigrationRule(
                visa_id=visa_map[visa_key].id,
                effective_from=datetime.now(),
                verified_at=datetime.now(),
                verified_by="system",
                **{k: v for k, v in rule_data.items() if k != 'visa_code'}
            )
            db.add(rule)
    
    # Seed occupations
    for occ_data in OCCUPATIONS:
        country_code = occ_data.pop('country_code')
        occ = OccupationMapping(
            country_id=country_map[country_code].id,
            **occ_data
        )
        db.add(occ)
    
    # Seed pathways
    for pathway_data in PATHWAYS_AU:
        visa_key = f"AU_{pathway_data['visa_code']}"
        if visa_key in visa_map:
            pathway = MigrationPathway(
                visa_id=visa_map[visa_key].id,
                **{k: v for k, v in pathway_data.items() if k != 'visa_code'}
            )
            db.add(pathway)
    
    for pathway_data in PATHWAYS_NZ:
        visa_key = f"NZ_{pathway_data['visa_code']}"
        if visa_key in visa_map:
            pathway = MigrationPathway(
                visa_id=visa_map[visa_key].id,
                **{k: v for k, v in pathway_data.items() if k != 'visa_code'}
            )
            db.add(pathway)
    
    db.commit()
