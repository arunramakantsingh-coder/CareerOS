"""Base model imports and common mixins."""
from datetime import datetime
from sqlalchemy import Column, DateTime
from app.core.database import Base

class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

__all__ = ["Base", "TimestampMixin"]
