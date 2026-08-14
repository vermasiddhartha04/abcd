from sqlalchemy.orm import Session

from app.models.upload import Upload
from app.services.ocr_service import process_ocr
from app.services.metadata_service import process_metadata
from app.services.analysis_service import process_analysis
from app.services.reply_service import process_reply


def process_document(
    db: Session,
    upload_id: int,
):
    # --------------------------------------------------
    # 1. Check Upload
    # --------------------------------------------------

    upload = (
        db.query(Upload)
        .filter(Upload.id == upload_id)
        .first()
    )

    if not upload:
        return None

    # --------------------------------------------------
    # 2. OCR
    # --------------------------------------------------

    ocr_result = process_ocr(
        db=db,
        upload_id=upload_id,
    )

    if not ocr_result:
        return None

    # --------------------------------------------------
    # 3. GST Metadata
    # --------------------------------------------------

    metadata = process_metadata(
        db=db,
        ocr_result_id=ocr_result.id,
    )

    if not metadata:
        return None

    # --------------------------------------------------
    # 4. AI Analysis
    # --------------------------------------------------

    analysis = process_analysis(
        db=db,
        metadata_id=metadata.id,
    )

    if not analysis:
        return None

    # --------------------------------------------------
    # 5. AI Reply
    # --------------------------------------------------

    reply = None

    if analysis.reply_required:
        reply = process_reply(
            db=db,
            analysis_id=analysis.id,
        )

    # --------------------------------------------------
    # Final Response
    # --------------------------------------------------

    return {
        "success": True,

        "upload_id": upload.id,

        "ocr_result_id": ocr_result.id,

        "metadata_id": metadata.id,

        "analysis_id": analysis.id,

        "reply_id": reply.id if reply else None,

        "metadata": {
            "gstin": metadata.gstin,
            "pan": metadata.pan,
            "taxpayer_name": metadata.taxpayer_name,
            "notice_number": metadata.notice_number,
            "document_type": metadata.document_type,
            "section": metadata.section,
            "financial_year": metadata.financial_year,
            "tax_period": metadata.tax_period,
            "tax_amount": str(metadata.tax_amount)
            if metadata.tax_amount is not None
            else None,
            "interest": str(metadata.interest)
            if metadata.interest is not None
            else None,
            "penalty": str(metadata.penalty)
            if metadata.penalty is not None
            else None,
        },

        "analysis": {
            "document_type": analysis.document_type,
            "summary": analysis.summary,
            "risk_level": analysis.risk_level,
            "reply_required": analysis.reply_required,
            "recommendation": analysis.recommendation,
        },

        "reply": (
            {
                "draft_reply": reply.draft_reply,
            }
            if reply
            else None
        ),
    }
