from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.process import ProcessDocumentResponse
from app.services.process_service import process_document


router = APIRouter(
    prefix="/process",
    tags=["Process Document"],
)


@router.post(
    "/{upload_id}",
    response_model=ProcessDocumentResponse,
)
def process_document_api(
    upload_id: int,
    db: Session = Depends(get_db),
):
    result = process_document(
        db=db,
        upload_id=upload_id,
    )

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Document processing failed or upload not found.",
        )

    return result
