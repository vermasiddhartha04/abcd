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
    # ========================================================
    # 1. Validate file name
    # ========================================================

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file selected.",
        )

    # ========================================================
    # 2. Validate file type
    # ========================================================

    if not allowed_file(file.filename):
        raise HTTPException(
            status_code=400,
            detail="Only PDF, DOC and DOCX files are allowed.",
        )

    # ========================================================
    # 3. Generate unique filename
    # ========================================================

    filename = generate_filename(file.filename)

    file_path = os.path.join(
        UPLOAD_DIR,
        filename,
    )

    # ========================================================
    # 4. Save physical file
    # ========================================================

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

    # ========================================================
    # 5. Save upload record in database
    #
    # Authentication is not being used currently.
    # uploaded_by=1 is used because the database column
    # currently has a NOT NULL constraint.
    # ========================================================

    upload = Upload(
        filename=filename,
        original_filename=file.filename,
        file_type=file.content_type or "application/octet-stream",
        file_path=file_path,
        case_id=case_id,
        uploaded_by=1,
    )

    # ========================================================
    # 6. Commit database record
    # ========================================================

    try:
        db.add(upload)
        db.commit()
        db.refresh(upload)

    except Exception as error:
        db.rollback()

        # Remove physical file if database save fails
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass

        raise HTTPException(
            status_code=500,
            detail=f"Failed to save upload record: {str(error)}",
        )

    # ========================================================
    # 7. Return upload information
    # ========================================================

    return upload