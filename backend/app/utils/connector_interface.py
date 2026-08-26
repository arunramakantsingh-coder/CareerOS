from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib
import json


class JobSourceConnector(ABC):
    """Abstract base class for job source connectors."""
    
    def __init__(self, source_id: str, config: Dict[str, Any]):
        self.source_id = source_id
        self.config = config
        self.name = self.__class__.__name__
    
    @abstractmethod
    async def fetch_listings(self, params: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Fetch job listings from the source.
        
        Returns:
            List of job listings with normalized fields
        """
        pass
    
    @abstractmethod
    async def validate_connection(self) -> bool:
        """
        Validate the connection to the source.
        
        Returns:
            True if connection is valid, False otherwise
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        Check the health of the source.
        
        Returns:
            Health status dictionary
        """
        pass
    
    def normalize_listing(self, raw_listing: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize a raw job listing to the standard format.
        
        Args:
            raw_listing: Raw listing from the source
            
        Returns:
            Normalized listing with standard fields
        """
        return {
            "external_id": self._get_external_id(raw_listing),
            "external_url": self._get_external_url(raw_listing),
            "title": self._get_title(raw_listing),
            "company": self._get_company(raw_listing),
            "location": self._get_location(raw_listing),
            "description": self._get_description(raw_listing),
            "posted_at": self._get_posted_at(raw_listing),
            "source_metadata": self._get_metadata(raw_listing),
            "fingerprint": self._generate_fingerprint(raw_listing)
        }
    
    def _get_external_id(self, listing: Dict) -> Optional[str]:
        """Extract external ID from listing."""
        return listing.get("id") or listing.get("job_id") or listing.get("external_id")
    
    def _get_external_url(self, listing: Dict) -> Optional[str]:
        """Extract external URL from listing."""
        return listing.get("url") or listing.get("link") or listing.get("external_url")
    
    def _get_title(self, listing: Dict) -> str:
        """Extract job title from listing."""
        return listing.get("title") or listing.get("job_title") or "Unknown Position"
    
    def _get_company(self, listing: Dict) -> Optional[str]:
        """Extract company name from listing."""
        return listing.get("company") or listing.get("company_name") or listing.get("employer")
    
    def _get_location(self, listing: Dict) -> Optional[str]:
        """Extract location from listing."""
        return listing.get("location") or listing.get("job_location") or listing.get("city")
    
    def _get_description(self, listing: Dict) -> Optional[str]:
        """Extract description from listing."""
        return listing.get("description") or listing.get("job_description") or listing.get("body")
    
    def _get_posted_at(self, listing: Dict) -> Optional[datetime]:
        """Extract posted date from listing."""
        posted = listing.get("posted_at") or listing.get("post_date") or listing.get("created_at")
        if posted and isinstance(posted, str):
            try:
                return datetime.fromisoformat(posted.replace("Z", "+00:00"))
            except:
                pass
        return posted if isinstance(posted, datetime) else None
    
    def _get_metadata(self, listing: Dict) -> Dict:
        """Extract source-specific metadata."""
        metadata = {k: v for k, v in listing.items() if k not in [
            "id", "job_id", "external_id", "url", "link", "external_url",
            "title", "job_title", "company", "company_name", "employer",
            "location", "job_location", "city", "description", "job_description",
            "body", "posted_at", "post_date", "created_at"
        ]}
        return metadata
    
    def _generate_fingerprint(self, listing: Dict) -> str:
        """
        Generate a unique fingerprint for deduplication.
        
        Uses a combination of title, company, and location to create a hash.
        """
        title = self._get_title(listing).strip().lower()
        company = (self._get_company(listing) or "").strip().lower()
        location = (self._get_location(listing) or "").strip().lower()
        
        # Clean and combine
        combined = f"{title}|{company}|{location}"
        
        # Generate hash
        return hashlib.md5(combined.encode()).hexdigest()
