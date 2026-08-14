from sqlalchemy.orm import Session

from app.models.metadata import Metadata
from app.models.ocr_result import OCRResult
from app.utils.gst_extractor import extract_gst_metadata


def process_metadata(
    db: Session,
    ocr_result_id: int,
):
    # --------------------------------------------------
    # Find OCR Result
    # --------------------------------------------------

    ocr_result = (
        db.query(OCRResult)
        .filter(OCRResult.id == ocr_result_id)
        .first()
    )

    if not ocr_result:
        return None

    # --------------------------------------------------
    # Extract GST Metadata
    # --------------------------------------------------

    data = extract_gst_metadata(
        ocr_result.extracted_text
    )

    # --------------------------------------------------
    # Check Existing Metadata
    # --------------------------------------------------

    metadata = (
        db.query(Metadata)
        .filter(
            Metadata.ocr_result_id == ocr_result.id
        )
        .first()
    )

    # --------------------------------------------------
    # If metadata already exists → UPDATE
    # --------------------------------------------------

    if metadata:

        metadata.gstin = data.get("gstin")
        metadata.pan = data.get("pan")
        metadata.taxpayer_name = data.get(
            "taxpayer_name"
        )
        metadata.notice_number = data.get(
            "notice_number"
        )
        metadata.document_type = data.get(
            "document_type"
        )
        metadata.section = data.get(
            "section"
        )
        metadata.financial_year = data.get(
            "financial_year"
        )
        metadata.tax_period = data.get(
            "tax_period"
        )
        metadata.tax_amount = data.get(
            "tax_amount"
        )
        metadata.interest = data.get(
            "interest"
        )
        metadata.penalty = data.get(
            "penalty"
        )

    # --------------------------------------------------
    # Otherwise → CREATE
    # --------------------------------------------------

    else:

        metadata = Metadata(
            ocr_result_id=ocr_result.id,

            gstin=data.get("gstin"),
            pan=data.get("pan"),
            taxpayer_name=data.get(
                "taxpayer_name"
            ),
            notice_number=data.get(
                "notice_number"
            ),
            document_type=data.get(
                "document_type"
            ),
            section=data.get(
                "section"
            ),
            financial_year=data.get(
                "financial_year"
            ),
            tax_period=data.get(
                "tax_period"
            ),
            tax_amount=data.get(
                "tax_amount"
            ),
            interest=data.get(
                "interest"
            ),
            penalty=data.get(
                "penalty"
            ),
        )

        db.add(metadata)

    # --------------------------------------------------
    # Save
    # --------------------------------------------------

    db.commit()
    db.refresh(metadata)

    return metadata