from sqlalchemy.orm import Session

from app.models.metadata import Metadata
from app.models.ocr_result import OCRResult
from app.utils.gst_extractor import extract_gst_metadata


def process_metadata(
    db: Session,
    ocr_result_id: int,
):
    # ==========================================================
    # 1. FIND OCR RESULT
    # ==========================================================

    ocr_result = (
        db.query(OCRResult)
        .filter(
            OCRResult.id == ocr_result_id
        )
        .first()
    )

    if not ocr_result:
        return None

    # ==========================================================
    # 2. EXTRACT GST METADATA
    # ==========================================================

    extracted_data = extract_gst_metadata(
        ocr_result.extracted_text or ""
    )

    # ==========================================================
    # 3. FIND EXISTING METADATA
    # ==========================================================

    metadata = (
        db.query(Metadata)
        .filter(
            Metadata.ocr_result_id == ocr_result.id
        )
        .first()
    )

    # ==========================================================
    # 4. COMMON VALUES
    # ==========================================================

    gstin = extracted_data.get("gstin")
    pan = extracted_data.get("pan")

    vendor = extracted_data.get(
        "vendor"
    )

    vendor_gstin = extracted_data.get(
        "vendor_gstin"
    )

    taxpayer_name = extracted_data.get(
        "taxpayer_name"
    )
    notice_number = extracted_data.get(
        "notice_number"
    )
    document_type = extracted_data.get(
        "document_type"
    )
    section = extracted_data.get(
        "section"
    )
    financial_year = extracted_data.get(
        "financial_year"
    )
    tax_period = extracted_data.get(
        "tax_period"
    )
    tax_amount = extracted_data.get(
        "tax_amount"
    )
    interest = extracted_data.get(
        "interest"
    )
    penalty = extracted_data.get(
        "penalty"
    )

    # ==========================================================
    # 5. UPDATE EXISTING METADATA
    # ==========================================================

    if metadata:

        metadata.gstin = gstin

        metadata.pan = pan

        metadata.vendor = vendor

        metadata.vendor_gstin = vendor_gstin

        metadata.taxpayer_name = (
            taxpayer_name
        )

        metadata.notice_number = (
            notice_number
        )

        metadata.document_type = (
            document_type
        )

        metadata.section = section

        metadata.financial_year = (
            financial_year
        )

        metadata.tax_period = (
            tax_period
        )

        metadata.tax_amount = (
            tax_amount
        )

        metadata.interest = (
            interest
        )

        metadata.penalty = (
            penalty
        )

    # ==========================================================
    # 6. CREATE NEW METADATA
    # ==========================================================

    else:

        metadata = Metadata(

            ocr_result_id=ocr_result.id,

            gstin=gstin,

            pan=pan,

            vendor=vendor,

            vendor_gstin=vendor_gstin,

            taxpayer_name=(
                taxpayer_name
            ),

            notice_number=(
                notice_number
            ),

            document_type=(
                document_type
            ),

            section=section,

            financial_year=(
                financial_year
            ),

            tax_period=(
                tax_period
            ),

            tax_amount=(
                tax_amount
            ),

            interest=(
                interest
            ),

            penalty=(
                penalty
            ),
        )

        db.add(metadata)

    # ==========================================================
    # 7. SAVE
    # ==========================================================

    db.commit()

    db.refresh(metadata)

    return metadata
