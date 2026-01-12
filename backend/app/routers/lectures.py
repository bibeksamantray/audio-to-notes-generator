import logging
from datetime import datetime
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from motor.motor_asyncio import AsyncIOMotorCollection

from .. import db
from ..config import settings
from ..models import LectureStatus
from ..schemas import LectureCreate, LectureDetail, LectureSummary, NotesGenerationResponse
from ..services.export_service import export_notes_as_pdf, export_notes_as_text
from ..services.notes_generator import generate_notes_with_ollama
from ..services.transcription import transcribe_audio

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/lectures", tags=["lectures"])


def get_lectures_collection_dep() -> AsyncIOMotorCollection:
    return db.get_lectures_collection()


@router.post(
    "",
    response_model=LectureDetail,
    summary="Upload a new lecture audio file and trigger transcription.",
)
async def create_lecture(
    title: str = Form(...),
    course: str | None = Form(None),
    lecturer: str | None = Form(None),
    lecture_date: str | None = Form(None),
    audio_file: UploadFile = File(...),
    lectures_col: AsyncIOMotorCollection = Depends(get_lectures_collection_dep),
):
    # 1. Store initial lecture document
    now = datetime.utcnow()
    lecture_doc = {
        "title": title,
        "course": course,
        "lecturer": lecturer,
        "lecture_date": lecture_date,
        "audio_file_path": "",
        "transcript_text": None,
        "transcript_language": None,
        "duration_seconds": None,
        "notes_text": None,
        "status": LectureStatus.TRANSCRIBING.value,
        "created_at": now,
        "updated_at": now,
        "error_message": None,
    }

    result = await lectures_col.insert_one(lecture_doc)
    lecture_id = result.inserted_id

    # 2. Save audio file to disk
    file_extension = Path(audio_file.filename or "").suffix or ".webm"
    audio_path = settings.AUDIO_DIR / f"{lecture_id}{file_extension}"

    try:
        with audio_path.open("wb") as f:
            f.write(await audio_file.read())
    except Exception as exc:
        logger.exception("Failed to save uploaded audio: %s", exc)
        await lectures_col.update_one(
            {"_id": lecture_id},
            {
                "$set": {
                    "status": LectureStatus.ERROR.value,
                    "error_message": f"Failed to save audio: {exc}",
                    "updated_at": datetime.utcnow(),
                }
            },
        )
        raise HTTPException(status_code=500, detail="Failed to save audio file.")

    await lectures_col.update_one(
        {"_id": lecture_id},
        {
            "$set": {
                "audio_file_path": str(audio_path),
                "updated_at": datetime.utcnow(),
            }
        },
    )

    # 3. Run transcription synchronously (simpler for project)
    try:
        transcript_text, language, duration = transcribe_audio(audio_path)
        await lectures_col.update_one(
            {"_id": lecture_id},
            {
                "$set": {
                    "transcript_text": transcript_text,
                    "transcript_language": language,
                    "duration_seconds": duration,
                    "status": LectureStatus.TRANSCRIBED.value,
                    "updated_at": datetime.utcnow(),
                }
            },
        )
    except Exception as exc:
        logger.exception("Transcription failed: %s", exc)
        await lectures_col.update_one(
            {"_id": lecture_id},
            {
                "$set": {
                    "status": LectureStatus.ERROR.value,
                    "error_message": f"Transcription failed: {exc}",
                    "updated_at": datetime.utcnow(),
                }
            },
        )
        raise HTTPException(status_code=500, detail="Transcription failed.")

    # 4. Return newly created lecture
    doc = await lectures_col.find_one({"_id": lecture_id})
    if not doc:
        raise HTTPException(status_code=500, detail="Lecture not found after creation.")

    return LectureDetail(**db.lecture_to_dict(doc))


@router.get(
    "",
    response_model=List[LectureSummary],
    summary="List all lectures with basic information.",
)
async def list_lectures(
    lectures_col: AsyncIOMotorCollection = Depends(get_lectures_collection_dep),
):
    cursor = lectures_col.find().sort("created_at", -1)
    lectures: list[LectureSummary] = []
    async for doc in cursor:
        lectures.append(
            LectureSummary(
                **db.lecture_to_dict(doc),
            )
        )
    return lectures


@router.get(
    "/{lecture_id}",
    response_model=LectureDetail,
    summary="Get full details for a specific lecture.",
)
async def get_lecture(
    lecture_id: str,
    lectures_col: AsyncIOMotorCollection = Depends(get_lectures_collection_dep),
):
    try:
        oid = db.object_id(lecture_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid lecture id.")

    doc = await lectures_col.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Lecture not found.")

    return LectureDetail(**db.lecture_to_dict(doc))


@router.post(
    "/{lecture_id}/generate-notes",
    response_model=NotesGenerationResponse,
    summary="Generate AI-powered lecture notes using local LLM.",
)
async def generate_notes(
    lecture_id: str,
    lectures_col: AsyncIOMotorCollection = Depends(get_lectures_collection_dep),
):
    try:
        oid = db.object_id(lecture_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid lecture id.")

    doc = await lectures_col.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Lecture not found.")

    if not doc.get("transcript_text"):
        raise HTTPException(status_code=400, detail="Transcript not available.")

    await lectures_col.update_one(
        {"_id": oid},
        {
            "$set": {
                "status": LectureStatus.GENERATING_NOTES.value,
                "updated_at": datetime.utcnow(),
            }
        },
    )

    try:
        notes_text = generate_notes_with_ollama(
            transcript=doc["transcript_text"],
            title=doc.get("title", ""),
            course=doc.get("course"),
            lecturer=doc.get("lecturer"),
            lecture_date=doc.get("lecture_date"),
        )

        await lectures_col.update_one(
            {"_id": oid},
            {
                "$set": {
                    "notes_text": notes_text,
                    "status": LectureStatus.COMPLETED.value,
                    "updated_at": datetime.utcnow(),
                }
            },
        )

        return NotesGenerationResponse(notes_text=notes_text)
    except Exception as exc:
        await lectures_col.update_one(
            {"_id": oid},
            {
                "$set": {
                    "status": LectureStatus.ERROR.value,
                    "error_message": f"Notes generation failed: {exc}",
                    "updated_at": datetime.utcnow(),
                }
            },
        )
        raise HTTPException(status_code=500, detail="Notes generation failed.")


@router.get(
    "/{lecture_id}/export",
    summary="Export notes for a lecture as PDF or plain text.",
)
async def export_notes(
    lecture_id: str,
    format: str = "pdf",
    lectures_col: AsyncIOMotorCollection = Depends(get_lectures_collection_dep),
):
    try:
        oid = db.object_id(lecture_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid lecture id.")

    doc = await lectures_col.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Lecture not found.")

    if not doc.get("notes_text"):
        raise HTTPException(status_code=400, detail="Notes not available.")

    title = doc.get("title", "Lecture Notes")
    notes_text = doc["notes_text"]

    if format == "txt":
        file_bytes, filename = export_notes_as_text(title, notes_text)
        media_type = "text/plain"
    elif format == "pdf":
        file_bytes, filename = export_notes_as_pdf(title, notes_text)
        media_type = "application/pdf"
    else:
        raise HTTPException(status_code=400, detail="Unsupported export format.")

    return StreamingResponse(
        iter([file_bytes]),
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

