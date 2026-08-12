"""Seed capability taxonomy data."""

CAPABILITY_TAXONOMY = [
    # Technical Capabilities
    {"name": "Network Architecture", "category": "Technical", "keywords": ["network design", "routing", "switching", "SD-WAN", "LAN", "WAN", "network topology"]},
    {"name": "Security Architecture", "category": "Technical", "keywords": ["security design", "firewall", "IPS", "IDS", "zero trust", "segmentation"]},
    {"name": "Cloud Architecture", "category": "Technical", "keywords": ["AWS", "Azure", "GCP", "cloud design", "cloud migration", "hybrid cloud"]},
    {"name": "Infrastructure Architecture", "category": "Technical", "keywords": ["infrastructure design", "data center", "server", "storage", "virtualization"]},
    {"name": "Cyber Security", "category": "Technical", "keywords": ["cybersecurity", "threat", "vulnerability", "security operations", "incident response"]},
    {"name": "Automation", "category": "Technical", "keywords": ["automation", "scripting", "CI/CD", "devops", "infrastructure as code"]},
    
    # Domain Capabilities
    {"name": "Financial Services", "category": "Domain", "keywords": ["banking", "insurance", "fintech", "trading", "payments", "financial"]},
    {"name": "Healthcare", "category": "Domain", "keywords": ["healthcare", "medical", "hospital", "clinical", "healthtech"]},
    {"name": "Telecommunications", "category": "Domain", "keywords": ["telecom", "5G", "mobile", "broadband", "network infrastructure"]},
    {"name": "Consulting", "category": "Domain", "keywords": ["consulting", "advisory", "strategy", "transformation", "client management"]},
    
    # Leadership Capabilities
    {"name": "People Leadership", "category": "Leadership", "keywords": ["team management", "mentoring", "hiring", "staff development", "performance management"]},
    {"name": "Strategic Leadership", "category": "Leadership", "keywords": ["strategy", "vision", "roadmap", "planning", "executive", "board"]},
    {"name": "Change Leadership", "category": "Leadership", "keywords": ["change management", "transformation", "digital transformation", "organizational change"]},
    {"name": "Vendor Management", "category": "Leadership", "keywords": ["vendor management", "procurement", "contracts", "RFP", "SLA", "supplier"]},
    
    # Governance Capabilities
    {"name": "IT Governance", "category": "Governance", "keywords": ["governance", "IT governance", "framework", "COBIT", "ITIL", "policy"]},
    {"name": "Risk Management", "category": "Governance", "keywords": ["risk", "risk assessment", "mitigation", "security risk", "operational risk"]},
    {"name": "Compliance", "category": "Governance", "keywords": ["compliance", "regulatory", "SOC2", "ISO", "GDPR", "HIPAA", "PCI"]},
    
    # Transformation Capabilities
    {"name": "Digital Transformation", "category": "Transformation", "keywords": ["digital transformation", "DX", "modernization", "innovation", "technology transformation"]},
    {"name": "Cloud Transformation", "category": "Transformation", "keywords": ["cloud migration", "cloud strategy", "cloud adoption", "cloud native"]},
    {"name": "Agile Transformation", "category": "Transformation", "keywords": ["agile", "scrum", "SAFe", "agile coaching", "lean"]},
]

def seed_capability_taxonomy(db):
    """Seed capability taxonomy data into database."""
    from app.models.capability_taxonomy import CapabilityTaxonomy
    
    for item in CAPABILITY_TAXONOMY:
        exists = db.query(CapabilityTaxonomy).filter(
            CapabilityTaxonomy.name == item["name"]
        ).first()
        
        if not exists:
            capability = CapabilityTaxonomy(**item)
            db.add(capability)
    
    db.commit()
