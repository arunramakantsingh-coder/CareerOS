from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import random

from app.utils.connector_interface import JobSourceConnector


class TestConnector(JobSourceConnector):
    """
    Test connector that generates sample job listings.
    
    This connector is safe to use for testing and development.
    It does not connect to any external services.
    """
    
    def __init__(self, source_id: str, config: Dict[str, Any]):
        super().__init__(source_id, config)
        self.sample_jobs = self._generate_sample_jobs()
    
    async def fetch_listings(self, params: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Fetch sample job listings.
        
        Args:
            params: Optional parameters (limit, offset, etc.)
        """
        limit = params.get("limit", 20) if params else 20
        return self.sample_jobs[:limit]
    
    async def validate_connection(self) -> bool:
        """Test connector is always valid."""
        return True
    
    async def health_check(self) -> Dict[str, Any]:
        """Return health status."""
        return {
            "status": "healthy",
            "source": self.name,
            "listings_count": len(self.sample_jobs)
        }
    
    def _generate_sample_jobs(self) -> List[Dict[str, Any]]:
        """Generate sample job listings for testing."""
        companies = [
            "TechCorp Inc.", "DataSphere Solutions", "CloudNova Systems",
            "SecureNet Technologies", "AI Innovators", "DevOps Masters",
            "InfraCloud Services", "CyberDefense Corp", "NextGen Solutions",
            "Digital Transformation Group", "Network Architects Ltd",
            "Security First Technologies"
        ]
        
        titles = [
            "Senior Network Architect", "Security Engineer", "Cloud Architect",
            "DevOps Engineer", "Infrastructure Manager", "Security Analyst",
            "Network Security Engineer", "Cloud Security Architect",
            "IT Director", "Systems Administrator", "Data Center Manager",
            "Network Operations Manager"
        ]
        
        locations = [
            "New York, NY", "San Francisco, CA", "Austin, TX",
            "Seattle, WA", "Boston, MA", "Chicago, IL",
            "Remote", "Hybrid", "London, UK", "Sydney, AU",
            "Singapore", "Dubai, UAE"
        ]
        
        descriptions = [
            "Design and implement secure network architectures. Lead security transformation initiatives.",
            "Manage cloud infrastructure and ensure security compliance. Implement zero trust architecture.",
            "Lead DevOps teams in CI/CD pipeline optimization. Automate infrastructure deployment.",
            "Oversee network operations and ensure high availability. Manage vendor relationships.",
            "Architect and deploy secure cloud solutions. Implement security best practices.",
            "Lead IT transformation projects. Manage team of 10+ engineers.",
            "Design and implement network security solutions. Manage firewall and security infrastructure.",
            "Lead cloud migration initiatives. Manage hybrid cloud environments.",
            "Oversee enterprise security strategy. Manage compliance and risk.",
            "Design and implement scalable network architectures. Optimize network performance."
        ]
        
        jobs = []
        for i in range(50):
            job_date = datetime.now() - timedelta(days=random.randint(0, 30))
            
            job = {
                "id": f"test_job_{i:04d}",
                "title": random.choice(titles),
                "company": random.choice(companies),
                "location": random.choice(locations),
                "description": random.choice(descriptions),
                "posted_at": job_date.isoformat(),
                "external_url": f"https://example.com/jobs/{i:04d}",
                "salary": f"${random.randint(80, 200)}k - ${random.randint(120, 250)}k",
                "job_type": random.choice(["Full-time", "Contract", "Part-time"]),
                "experience_level": random.choice(["Senior", "Mid", "Lead", "Entry"]),
                "source_metadata": {
                    "test_data": True,
                    "generated": datetime.now().isoformat()
                }
            }
            jobs.append(job)
        
        return jobs
