from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.ocr_result import OCRResult
from app.models.upload import Upload
from app.utils.pdf_reader import extract_text_from_pdf


def process_ocr(
    db: Session,
    upload_id: int,
):
    # Find uploaded document
    upload = (
        db.query(Upload)
        .filter(Upload.id == upload_id)
        .first()
    )

    if not upload:
        return None

    # Check file exists
    import os

    if not os.path.exists(upload.file_path):
        raise HTTPException(
            status_code=404,
            detail="Uploaded file not found on server.",
        )

    # Currently supporting PDF text extraction
    if upload.file_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="OCR currently supports PDF files only.",
        )

    # Extract text
    extracted_text = extract_text_from_pdf(
        upload.file_path
    )

    if not extracted_text.strip():
        raise HTTPException(
            status_code=400,
            detail="No text could be extracted from this PDF.",
        )

    # Save OCR result
    ocr = OCRResult(
        upload_id=upload.id,
        extracted_text=extracted_text,
    )

    db.add(ocr)
    db.commit()
    db.refresh(ocr)

    return ocr