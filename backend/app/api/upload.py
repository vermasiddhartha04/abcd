from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.upload import UploadResponse
from app.services.upload_service import save_upload


router = APIRouter(
    prefix="/uploads",
    tags=["Document Upload"],
)


@router.post(
    "/",
    response_model=UploadResponse,
)
def upload_document(
    case_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    return save_upload(
        db=db,
        file=file,
        case_id=case_id,
    )