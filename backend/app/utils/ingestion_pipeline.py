from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from sqlalchemy.orm import Session

from app.models.job_source import JobSource
from app.models.job_listing import JobListing
from app.utils.connector_interface import JobSourceConnector

logger = logging.getLogger(__name__)


class IngestionPipeline:
    """Job ingestion pipeline for processing listings from sources."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def ingest_from_connector(
        self,
        source: JobSource,
        connector: JobSourceConnector,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Ingest job listings from a connector.
        
        Args:
            source: JobSource database object
            connector: JobSourceConnector instance
            params: Optional parameters for fetching
            
        Returns:
            Ingestion statistics
        """
        stats = {
            "fetched": 0,
            "created": 0,
            "updated": 0,
            "duplicates": 0,
            "errors": 0
        }
        
        try:
            # Fetch listings
            raw_listings = await connector.fetch_listings(params)
            stats["fetched"] = len(raw_listings)
            
            for raw_listing in raw_listings:
                try:
                    # Normalize listing
                    normalized = connector.normalize_listing(raw_listing)
                    
                    # Check for duplicates
                    existing = self._find_existing_listing(normalized)
                    
                    if existing:
                        # Update existing listing
                        self._update_listing(existing, normalized)
                        stats["updated"] += 1
                    else:
                        # Create new listing
                        self._create_listing(source, normalized)
                        stats["created"] += 1
                
                except Exception as e:
                    logger.error(f"Error processing listing: {e}")
                    stats["errors"] += 1
            
            # Update source
            source.last_sync = datetime.now()
            source.sync_status = "success"
            source.total_listings = stats["created"] + stats["updated"]
            
        except Exception as e:
            logger.error(f"Error ingesting from connector: {e}")
            source.sync_status = "failed"
            source.last_error = str(e)
            stats["errors"] += 1
        
        self.db.commit()
        return stats
    
    def _find_existing_listing(self, normalized: Dict) -> Optional[JobListing]:
        """Find an existing listing by fingerprint or external ID."""
        fingerprint = normalized.get("fingerprint")
        external_id = normalized.get("external_id")
        
        if fingerprint:
            existing = self.db.query(JobListing).filter(
                JobListing.fingerprint == fingerprint,
                JobListing.status == "active"
            ).first()
            if existing:
                return existing
        
        if external_id:
            existing = self.db.query(JobListing).filter(
                JobListing.external_id == external_id,
                JobListing.status == "active"
            ).first()
            if existing:
                return existing
        
        return None
    
    def _create_listing(self, source: JobSource, normalized: Dict) -> JobListing:
        """Create a new job listing."""
        listing = JobListing(
            source_id=source.id,
            user_id=source.user_id,
            external_id=normalized.get("external_id"),
            external_url=normalized.get("external_url"),
            title=normalized.get("title", "Unknown Position"),
            company=normalized.get("company"),
            location=normalized.get("location"),
            description=normalized.get("description"),
            posted_at=normalized.get("posted_at"),
            source_metadata=normalized.get("source_metadata", {}),
            fingerprint=normalized.get("fingerprint"),
            status="active",
            last_seen_at=datetime.now()
        )
        self.db.add(listing)
        return listing
    
    def _update_listing(self, existing: JobListing, normalized: Dict) -> JobListing:
        """Update an existing job listing."""
        existing.title = normalized.get("title", existing.title)
        existing.company = normalized.get("company") or existing.company
        existing.location = normalized.get("location") or existing.location
        existing.description = normalized.get("description") or existing.description
        existing.external_url = normalized.get("external_url") or existing.external_url
        existing.last_seen_at = datetime.now()
        
        if normalized.get("posted_at"):
            existing.posted_at = normalized.get("posted_at")
        
        return existing
