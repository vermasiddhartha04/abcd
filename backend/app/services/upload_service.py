import os
import shutil

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.models.upload import Upload
from app.utils.file_utils import (
    allowed_file,
    generate_filename,
)


UPLOAD_DIR = "app/uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)


def save_upload(
    db: Session,
    file: UploadFile,
    case_id: int,
):
    # -----------------------------
    # Validate file name
    # -----------------------------
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file selected.",
        )

    # -----------------------------
    # Validate file type
    # -----------------------------
    if not allowed_file(file.filename):
        raise HTTPException(
            status_code=400,
            detail="Only PDF, DOC and DOCX files are allowed.",
        )

    # -----------------------------
    # Generate unique filename
    # -----------------------------
    filename = generate_filename(file.filename)

    file_path = os.path.join(
        UPLOAD_DIR,
        filename,
    )

    # -----------------------------
    # Save file
    # -----------------------------
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer,
            )
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"File upload failed: {str(error)}",
        )

    # -----------------------------
    # Save database record
    # -----------------------------
    upload = Upload(
        filename=filename,
        original_filename=file.filename,
        file_type=file.content_type or "application/octet-stream",
        file_path=file_path,
        case_id=case_id,
        uploaded_by=None,
    )

    db.add(upload)
    db.commit()
    db.refresh(upload)

    return upload