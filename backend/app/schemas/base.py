from pydantic import BaseModel
from datetime import datetime


class BaseResponse(BaseModel):
    """Base response schema with timestamps."""
    created_at: datetime
    updated_at: datetime
