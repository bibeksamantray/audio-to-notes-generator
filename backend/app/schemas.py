from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from .models import LectureStatus


class LectureCreate(BaseModel):
    """Payload for creating a new lecture with an uploaded audio file."""

    title: str
    course: Optional[str] = None
    lecturer: Optional[str] = None
    lecture_date: Optional[str] = None  # ISO date string for simplicity


class LectureSummary(BaseModel):
    """Lightweight view for listing lectures."""

    id: str
    title: str
    course: Optional[str]
    lecturer: Optional[str]
    lecture_date: Optional[str]
    status: LectureStatus
    created_at: datetime
    updated_at: datetime


class LectureDetail(LectureSummary):
    """Detailed view for a single lecture."""

    audio_file_path: str
    transcript_text: Optional[str] = None
    transcript_language: Optional[str] = None
    duration_seconds: Optional[float] = None
    notes_text: Optional[str] = None
    error_message: Optional[str] = None


class NotesGenerationResponse(BaseModel):
    """Response returned after generating notes with the LLM."""

    notes_text: str
    status: LectureStatus = Field(default=LectureStatus.COMPLETED)

