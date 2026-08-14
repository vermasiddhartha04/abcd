from sqlalchemy.orm import Session

from app.models.analysis import Analysis
from app.models.metadata import Metadata
from app.models.ocr_result import OCRResult
from app.utils.analysis_engine import analyze_notice


def process_analysis(
    db: Session,
    metadata_id: int,
):
    """
    Process GST litigation analysis.

    Supports:
    - SCN
    - OIO
    - Appeal
    - OIA
    - DRC
    - Unknown
    """

    # ==========================================================
    # 1. Find Metadata
    # ==========================================================

    metadata = (
        db.query(Metadata)
        .filter(
            Metadata.id == metadata_id
        )
        .first()
    )

    if not metadata:
        return None

    # ==========================================================
    # 2. Find OCR Result
    # ==========================================================

    ocr_result = (
        db.query(OCRResult)
        .filter(
            OCRResult.id == metadata.ocr_result_id
        )
        .first()
    )

    if not ocr_result:
        return None

    # ==========================================================
    # 3. Complete Metadata
    # ==========================================================

    metadata_dict = {
        "gstin": metadata.gstin,
        "pan": metadata.pan,
        "taxpayer_name": metadata.taxpayer_name,
        "notice_number": metadata.notice_number,
        "document_type": metadata.document_type,
        "section": metadata.section,
        "financial_year": metadata.financial_year,
        "tax_period": metadata.tax_period,
        "tax_amount": metadata.tax_amount,
        "interest": metadata.interest,
        "penalty": metadata.penalty,
    }

    # ==========================================================
    # 4. Analysis Engine
    # ==========================================================

    result = analyze_notice(
        text=ocr_result.extracted_text,
        metadata=metadata_dict,
    )

    # ==========================================================
    # 5. Existing Analysis
    # ==========================================================

    analysis = (
        db.query(Analysis)
        .filter(
            Analysis.metadata_id == metadata.id
        )
        .first()
    )

    # ==========================================================
    # 6. Update Existing
    # ==========================================================

    if analysis:

        analysis.document_type = result.get(
            "document_type"
        )

        analysis.summary = result.get(
            "summary"
        )

        analysis.risk_level = result.get(
            "risk_level"
        )

        analysis.reply_required = result.get(
            "reply_required",
            False,
        )

        analysis.recommendation = result.get(
            "recommendation"
        )

    # ==========================================================
    # 7. Create New
    # ==========================================================

    else:

        analysis = Analysis(
            metadata_id=metadata.id,
            document_type=result.get(
                "document_type"
            ),
            summary=result.get(
                "summary"
            ),
            risk_level=result.get(
                "risk_level"
            ),
            reply_required=result.get(
                "reply_required",
                False,
            ),
            recommendation=result.get(
                "recommendation"
            ),
        )

        db.add(analysis)

    # ==========================================================
    # 8. Save
    # ==========================================================

    db.commit()

    db.refresh(analysis)

    return analysis