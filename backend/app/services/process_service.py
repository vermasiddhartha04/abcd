from sqlalchemy.orm import Session

from app.models.upload import Upload

from app.services.ocr_service import process_ocr
from app.services.metadata_service import process_metadata
from app.services.analysis_service import process_analysis
from app.services.reply_service import process_reply

from app.utils.analysis_engine import analyze_notice


def process_document(
    db: Session,
    upload_id: int,
):
    """
    Complete GST Litigation processing pipeline.

    Flow:

    Upload
      ↓
    OCR
      ↓
    GST Metadata
      ↓
    Document Classification
      ↓
    Analysis
      ↓
    Next Action

    SCN
      ↓
    SCN Reply
      ↓
    OIO

    OIO
      ↓
    Appeal

    Appeal
      ↓
    OIA

    OIA
      ↓
    Final Review
    """

    # ==========================================================
    # 1. FIND UPLOAD
    # ==========================================================

    upload = (
        db.query(Upload)
        .filter(
            Upload.id == upload_id
        )
        .first()
    )

    if not upload:
        return None

    # ==========================================================
    # 2. OCR
    # ==========================================================

    ocr_result = process_ocr(
        db=db,
        upload_id=upload_id,
    )

    if not ocr_result:
        return None

    # ==========================================================
    # 3. GST METADATA
    # ==========================================================

    metadata = process_metadata(
        db=db,
        ocr_result_id=ocr_result.id,
    )

    if not metadata:
        return None

    # ==========================================================
    # 4. ANALYSIS
    # ==========================================================

    analysis = process_analysis(
        db=db,
        metadata_id=metadata.id,
    )

    if not analysis:
        return None

    # ==========================================================
    # 5. COMPLETE METADATA FOR WORKFLOW
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
    # 6. RUN WORKFLOW ANALYSIS
    # ==========================================================

    workflow_analysis = analyze_notice(
        text=ocr_result.extracted_text,
        metadata=metadata_dict,
    )

    document_type = workflow_analysis.get(
        "document_type",
        analysis.document_type,
    )

    risk_level = workflow_analysis.get(
        "risk_level",
        analysis.risk_level,
    )

    reply_required = workflow_analysis.get(
        "reply_required",
        analysis.reply_required,
    )

    appeal_required = workflow_analysis.get(
        "appeal_required",
        False,
    )

    action_type = workflow_analysis.get(
        "action_type"
    )

    action_label = workflow_analysis.get(
        "action_label"
    )

    next_stage = workflow_analysis.get(
        "next_stage"
    )

    # ==========================================================
    # 7. DOCUMENT-SPECIFIC DRAFT
    # ==========================================================

    draft_required = document_type in {
        "SCN",
        "OIO",
        "APPEAL",
        "OIA",
    }

    reply = None

    if draft_required:
        reply = process_reply(
            db=db,
            analysis_id=analysis.id,
            document_type=document_type,
        )

    # ==========================================================
    # 8. FINAL DOCUMENT INFORMATION
    # ==========================================================

    document = {
        "document_type": document_type,
        "current_stage": document_type,
        "next_stage": next_stage,
        "action_type": action_type,
        "action_label": action_label,
    }

    # ==========================================================
    # 9. METADATA
    # ==========================================================

    metadata_response = {
        "gstin": metadata.gstin,
        "pan": metadata.pan,
        "taxpayer_name": metadata.taxpayer_name,
        "notice_number": metadata.notice_number,
        "document_type": document_type,
        "section": metadata.section,
        "financial_year": metadata.financial_year,
        "tax_period": metadata.tax_period,
        "tax_amount": (
            str(metadata.tax_amount)
            if metadata.tax_amount is not None
            else None
        ),
        "interest": (
            str(metadata.interest)
            if metadata.interest is not None
            else None
        ),
        "penalty": (
            str(metadata.penalty)
            if metadata.penalty is not None
            else None
        ),
    }

    # ==========================================================
    # 10. ANALYSIS
    # ==========================================================

    analysis_response = {
        "document_type": document_type,

        "summary": analysis.summary,

        "risk_level": risk_level,

        "reply_required": reply_required,

        "appeal_required": appeal_required,

        "recommendation": analysis.recommendation,

        "sections": workflow_analysis.get(
            "sections",
            [],
        ),

        "action_type": action_type,

        "action_label": action_label,

        "next_stage": next_stage,
    }

    # ==========================================================
    # 11. DRAFT RESPONSE
    # ==========================================================

    reply_response = None

    if reply:

        reply_response = {
            "id": reply.id,
            "document_type": document_type,
            "draft_reply": reply.draft_reply,
        }

    # ==========================================================
    # 12. LITIGATION WORKFLOW
    # ==========================================================

    litigation = {

        "current_stage": document_type,

        "next_stage": next_stage,

        "action_required": (
            action_type is not None
        ),

        "action_type": action_type,

        "action_label": action_label,

        "workflow": [
            "SCN",
            "SCN_REPLY",
            "OIO",
            "APPEAL",
            "OIA",
            "FINAL",
        ],
    }

    # ==========================================================
    # 13. FINAL RESPONSE
    # ==========================================================

    return {

        "success": True,

        "upload_id": upload.id,

        "ocr_result_id": ocr_result.id,

        "metadata_id": metadata.id,

        "analysis_id": analysis.id,

        "reply_id": (
            reply.id
            if reply
            else None
        ),

        "document": document,

        "metadata": metadata_response,

        "analysis": analysis_response,

        "reply": reply_response,

        "litigation": litigation,
    }