import os
from pathlib import Path

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.ocr_result import OCRResult
from app.models.upload import Upload
from app.utils.pdf_reader import extract_text_from_pdf


# ==========================================================
# PROJECT ROOT
# ==========================================================

BACKEND_DIR = Path(
    __file__
).resolve().parents[1]


# ==========================================================
# RESOLVE UPLOAD PATH
# ==========================================================

def resolve_upload_path(
    file_path: str,
) -> Path:

    if not file_path:

        raise HTTPException(
            status_code=404,
            detail="Uploaded file path is missing.",
        )

    raw_path = Path(
        str(file_path)
    )

    # ------------------------------------------------------
    # 1. Absolute path
    # ------------------------------------------------------

    if raw_path.is_absolute():

        if raw_path.exists():

            return raw_path

    # ------------------------------------------------------
    # 2. Relative to backend directory
    # ------------------------------------------------------

    backend_path = (
        BACKEND_DIR
        / raw_path
    )

    if backend_path.exists():

        return backend_path

    # ------------------------------------------------------
    # 3. Relative to current working directory
    # ------------------------------------------------------

    cwd_path = (
        Path.cwd()
        / raw_path
    )

    if cwd_path.exists():

        return cwd_path

    # ------------------------------------------------------
    # 4. Normalize Windows separators
    # ------------------------------------------------------

    normalized = str(
        file_path
    ).replace(
        "\\",
        os.sep,
    )

    normalized_path = Path(
        normalized
    )

    if normalized_path.is_absolute():

        if normalized_path.exists():

            return normalized_path

    backend_normalized = (
        BACKEND_DIR
        / normalized_path
    )

    if backend_normalized.exists():

        return backend_normalized

    # ------------------------------------------------------
    # File not found
    # ------------------------------------------------------

    raise HTTPException(
        status_code=404,
        detail=(
            "Uploaded file not found on server. "
            f"Expected path: {file_path}"
        ),
    )


# ==========================================================
# PROCESS OCR
# ==========================================================

def process_ocr(
    db: Session,
    upload_id: int,
):

    # ------------------------------------------------------
    # FIND UPLOAD
    # ------------------------------------------------------

    upload = (
        db.query(Upload)
        .filter(
            Upload.id == upload_id
        )
        .first()
    )

    if not upload:

        return None

    # ------------------------------------------------------
    # VALIDATE FILE TYPE
    # ------------------------------------------------------

    if (
        upload.file_type
        != "application/pdf"
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "OCR currently supports "
                "PDF files only."
            ),
        )

    # ------------------------------------------------------
    # RESOLVE FILE
    # ------------------------------------------------------

    file_path = resolve_upload_path(
        upload.file_path
    )

    print("")
    print(
        "=========================================="
    )
    print("OCR PROCESSING")
    print(
        "=========================================="
    )
    print(
        "Upload ID:",
        upload.id,
    )
    print(
        "Original filename:",
        upload.original_filename,
    )
    print(
        "Stored filename:",
        upload.filename,
    )
    print(
        "Resolved path:",
        file_path,
    )
    print(
        "File exists:",
        file_path.exists(),
    )
    print(
        "=========================================="
    )

    # ------------------------------------------------------
    # EXTRACT TEXT
    # ------------------------------------------------------

    try:

        extracted_text = (
            extract_text_from_pdf(
                str(file_path)
            )
        )

    except HTTPException:

        raise

    except Exception as exc:

        print(
            "OCR extraction error:",
            repr(exc),
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "OCR processing failed: "
                f"{str(exc)}"
            ),
        )

    # ------------------------------------------------------
    # VALIDATE OCR RESULT
    # ------------------------------------------------------

    extracted_text = (
        extracted_text
        or ""
    ).strip()

    if not extracted_text:

        raise HTTPException(
            status_code=400,
            detail=(
                "No text could be extracted "
                "from this PDF."
            ),
        )

    print("")
    print(
        "=========================================="
    )
    print("OCR SUCCESS")
    print(
        "=========================================="
    )
    print(
        "Characters:",
        len(extracted_text),
    )
    print(
        "=========================================="
    )

    # ------------------------------------------------------
    # CHECK EXISTING OCR
    # ------------------------------------------------------

    existing = (
        db.query(OCRResult)
        .filter(
            OCRResult.upload_id
            == upload.id
        )
        .order_by(
            OCRResult.id.desc()
        )
        .first()
    )

    # ------------------------------------------------------
    # UPDATE EXISTING
    # ------------------------------------------------------

    if existing:

        existing.extracted_text = (
            extracted_text
        )

        db.commit()

        db.refresh(
            existing
        )

        print(
            "Existing OCR result updated."
        )

        return existing

    # ------------------------------------------------------
    # CREATE NEW OCR RESULT
    # ------------------------------------------------------

    ocr = OCRResult(
        upload_id=upload.id,
        extracted_text=extracted_text,
    )

    db.add(
        ocr
    )

    db.commit()

    db.refresh(
        ocr
    )

    print(
        "New OCR result created."
    )

    print(
        "OCR Result ID:",
        ocr.id,
    )

    return ocr
