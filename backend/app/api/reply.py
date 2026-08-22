from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.reply_service import process_reply


router = APIRouter(
    prefix="/reply",
    tags=["Reply"],
)


# ==========================================================
# GENERATE REPLY
# ==========================================================

@router.post(
    "/{metadata_id}"
)
def generate_reply(
    metadata_id: int,
    db: Session = Depends(
        get_db
    ),
):

    result = process_reply(
        db=db,
        metadata_id=metadata_id,
    )

    if not result:

        raise HTTPException(
            status_code=404,
            detail=(
                "Metadata not found or "
                "OCR result unavailable."
            ),
        )

    quality = result.get(
        "quality",
        {},
    )

    reply_record = result.get(
        "reply"
    )

    return {
        "success": True,

        "reply_id": (
            reply_record.id
            if reply_record
            else None
        ),

        "metadata_id": metadata_id,

        "document_type": (
            "SCN_REPLY"
        ),

        "reply": result.get(
            "reply_text",
            "",
        ),

        "quality": quality,

        "word_count": result.get(
            "word_count",
            0,
        ),

        "character_count": result.get(
            "character_count",
            0,
        ),

        "estimated_pages": result.get(
            "estimated_pages",
            0,
        ),

        "issue_analysis": result.get(
            "issue_analysis",
            {},
        ),

        "legal_mapping": result.get(
            "legal_mapping",
            {},
        ),

        "evidence_mapping": result.get(
            "evidence_mapping",
            {},
        ),

        "reply_structure": result.get(
            "reply_structure",
            [],
        ),

        "docx_available": bool(
            result.get(
                "docx_path"
            )
        ),
    }


# ==========================================================
# DOWNLOAD GENERATED DOCX
# ==========================================================

@router.get(
    "/{metadata_id}/download"
)
def download_reply(
    metadata_id: int,
    db: Session = Depends(
        get_db
    ),
):

    result = process_reply(
        db=db,
        metadata_id=metadata_id,
    )

    if not result:

        raise HTTPException(
            status_code=404,
            detail=(
                "Reply not found or "
                "could not be generated."
            ),
        )

    docx_path = result.get(
        "docx_path"
    )

    if not docx_path:

        raise HTTPException(
            status_code=404,
            detail=(
                "Reply DOCX file is not available."
            ),
        )

    return FileResponse(
        path=docx_path,
        media_type=(
            "application/vnd.openxmlformats-"
            "officedocument.wordprocessingml.document"
        ),
        filename=(
            "SCN_REPLY.docx"
        ),
    )
