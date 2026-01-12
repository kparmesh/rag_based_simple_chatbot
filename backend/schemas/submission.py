from pydantic import BaseModel
from datetime import datetime


class SubmissionBase(BaseModel):
    """Base submission schema."""
    questionnaire_title: str
    step: int = 1
    is_complete: bool = False


class SubmissionCreate(SubmissionBase):
    """Schema for creating a submission."""
    user_id: str | None = None


class SubmissionResponse(SubmissionBase):
    """Schema for submission response."""
    id: int
    user_id: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

