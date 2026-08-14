from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.ocr import OCRResultResponse
from app.services.ocr_service import process_ocr


router = APIRouter(
    prefix="/ocr",
    tags=["OCR"],
)


@router.post(
    "/{upload_id}",
    response_model=OCRResultResponse,
)
def run_ocr(
    upload_id: int,
    db: Session = Depends(get_db),
):
    result = process_ocr(
        db=db,
        upload_id=upload_id,
    )

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Upload not found",
        )

    return result