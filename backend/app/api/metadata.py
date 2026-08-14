from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.metadata import MetadataResponse
from app.services.metadata_service import process_metadata


router = APIRouter(
    prefix="/metadata",
    tags=["GST Metadata"],
)


@router.post(
    "/{ocr_result_id}",
    response_model=MetadataResponse,
)
def generate_metadata(
    ocr_result_id: int,
    db: Session = Depends(get_db),
):
    metadata = process_metadata(
        db=db,
        ocr_result_id=ocr_result_id,
    )

    if not metadata:
        raise HTTPException(
            status_code=404,
            detail="OCR Result not found",
        )

    return metadata