from pathlib import Path
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models.reply import Reply
from app.models.metadata import Metadata
from app.models.ocr_result import OCRResult
from app.models.analysis import Analysis

from app.utils.reply_engine import (
    generate_scn_reply,
)

from app.utils.reply_structure import (
    build_reply_structure,
)

from app.utils.reply_quality import (
    evaluate_reply_quality,
)

from app.utils.issue_engine import (
    build_issue_analysis,
)

from app.utils.legal_mapper import (
    build_legal_mapping,
)

from app.utils.evidence_mapper import (
    map_evidence_to_issues,
)

from app.services.reply_document_service import (
    create_reply_docx,
)


# ==========================================================
# METADATA DICT
# ==========================================================

def _metadata_to_dict(
    metadata: Metadata,
    analysis: Optional[Analysis] = None,
) -> Dict[str, Any]:

    return {
        "gstin": metadata.gstin,
        "pan": metadata.pan,

        "taxpayer_name":
            metadata.taxpayer_name,

        "notice_number":
            metadata.notice_number,

        "document_type":
            metadata.document_type,

        "section":
            metadata.section,

        "financial_year":
            metadata.financial_year,

        "tax_period":
            metadata.tax_period,

        "tax_amount":
            metadata.tax_amount,

        "interest":
            metadata.interest,

        "penalty":
            metadata.penalty,

        # --------------------------------------------------
        # Vendor / Supplier
        # --------------------------------------------------

        "vendor":
            metadata.vendor,

        "vendor_gstin":
            metadata.vendor_gstin,

        # --------------------------------------------------
        # Structured litigation analysis
        # --------------------------------------------------

        "demands":
            (
                analysis.demands
                if analysis
                else []
            ),

        # Total proposed demand from structured analysis
        "total_demand": (
            sum(
                float(item.get("amount") or 0)
                for item in (
                    analysis.demands
                    if analysis
                    else []
                )
                if isinstance(item, dict)
            )
        ),

        "penalty_proposals":
            (
                analysis.penalty_proposals
                if analysis
                else []
            ),

        "allegations":
            (
                analysis.allegations
                if analysis
                else []
            ),
    }


# ==========================================================
# FIND OCR
# ==========================================================

def _get_ocr_result(
    db: Session,
    metadata: Metadata,
) -> Optional[OCRResult]:

    return (
        db.query(OCRResult)
        .filter(
            OCRResult.id
            == metadata.ocr_result_id
        )
        .first()
    )


# ==========================================================
# PROCESS REPLY
# ==========================================================

def process_reply(
    db: Session,
    metadata_id: int,
):
    """
    Generate the detailed SCN reply for a Metadata record.

    Pipeline:

        Metadata
            ↓
        OCR text
            ↓
        Issue analysis
            ↓
        Legal mapping
            ↓
        Evidence mapping
            ↓
        Reply engine
            ↓
        Quality validation
            ↓
        Database Reply
            ↓
        DOCX
    """

    # ------------------------------------------------------
    # 1. FIND METADATA
    # ------------------------------------------------------

    metadata = (
        db.query(Metadata)
        .filter(
            Metadata.id
            == metadata_id
        )
        .first()
    )

    if not metadata:
        return None

    # ------------------------------------------------------
    # 2. FIND OCR
    # ------------------------------------------------------

    ocr_result = _get_ocr_result(
        db,
        metadata,
    )

    if not ocr_result:
        return None

    text = (
        ocr_result.extracted_text
        or ""
    )

    # ------------------------------------------------------
    # 3. FIND ANALYSIS
    # ------------------------------------------------------

    analysis = (
        db.query(Analysis)
        .filter(
            Analysis.metadata_id
            == metadata.id
        )
        .order_by(
            Analysis.id.desc()
        )
        .first()
    )

    if not analysis:
        return None

    # ------------------------------------------------------
    # 4. COMPLETE METADATA / ANALYSIS DICT
    # ------------------------------------------------------

    metadata_dict = (
        _metadata_to_dict(
            metadata,
            analysis,
        )
    )

    # ------------------------------------------------------
    # 5. ISSUE ANALYSIS
    # ------------------------------------------------------

    issue_analysis = (
        build_issue_analysis(
            text=text,
            metadata=metadata_dict,
        )
    )

    issues = issue_analysis.get(
        "issues",
        [],
    )

    # ------------------------------------------------------
    # 4. LEGAL MAPPING
    # ------------------------------------------------------

    legal_mapping = (
        build_legal_mapping(
            text=text,
            issues=issues,
        )
    )

    # ------------------------------------------------------
    # 5. EVIDENCE MAPPING
    # ------------------------------------------------------

    evidence_mapping = (
        map_evidence_to_issues(
            text=text,
            issues=issues,
        )
    )

    # ------------------------------------------------------
    # 6. REPLY STRUCTURE
    # ------------------------------------------------------

    reply_structure = (
        build_reply_structure(
            metadata=metadata_dict,
            issue_analysis=issue_analysis,
            legal_mapping=legal_mapping,
            evidence_mapping=evidence_mapping,
        )
    )

    # ------------------------------------------------------
    # 7. GENERATE REPLY
    # ------------------------------------------------------

    generated = generate_scn_reply(
        text=text,
        metadata=metadata_dict,
    )

    reply_text = (
        generated.get(
            "reply",
            "",
        )
    )

    # ------------------------------------------------------
    # 8. QUALITY CHECK
    # ------------------------------------------------------

    quality_report = (
        evaluate_reply_quality(
            reply=reply_text,
            metadata=metadata_dict,
            issue_analysis=issue_analysis,
            legal_mapping=legal_mapping,
            evidence_mapping=evidence_mapping,
        )
    )

    # ------------------------------------------------------
    # 10. ANALYSIS RECORD
    #
    # Already loaded before the reply pipeline so that
    # structured litigation data is available to all
    # reply components.
    # ------------------------------------------------------

    # ------------------------------------------------------
    # 10. FIND EXISTING REPLY
    #
    # Reply is linked to Analysis, not Metadata.
    # Existing database relationship:
    #
    # Reply.analysis_id -> Analysis.id
    # ------------------------------------------------------

    reply_record = (
        db.query(Reply)
        .filter(
            Reply.analysis_id
            == analysis.id
        )
        .first()
    )

    # ------------------------------------------------------
    # 11. CREATE / UPDATE
    # ------------------------------------------------------

    if reply_record:

        reply_record.draft_reply = (
            reply_text
        )

    else:

        reply_record = Reply(
            analysis_id=analysis.id,
            draft_reply=reply_text,
        )

        db.add(
            reply_record
        )

    # ------------------------------------------------------
    # 12. SAVE REPLY
    # ------------------------------------------------------

    db.commit()

    db.refresh(
        reply_record
    )

    # ------------------------------------------------------
    # 13. CREATE DOCX
    # ------------------------------------------------------

    metadata_dict[
        "reply_id"
    ] = reply_record.id

    docx_path = create_reply_docx(
        reply=reply_text,
        metadata=metadata_dict,
        upload_id=(
            getattr(
                metadata,
                "upload_id",
                None,
            )
        ),
        reply_id=reply_record.id,
    )

    # ------------------------------------------------------
    # 14. RETURN COMPLETE RESULT
    # ------------------------------------------------------

    return {
        "reply": reply_record,
        "reply_text": reply_text,
        "docx_path": docx_path,
        "issue_analysis": issue_analysis,
        "legal_mapping": legal_mapping,
        "evidence_mapping": evidence_mapping,
        "reply_structure": reply_structure,
        "quality": quality_report,
        "word_count": quality_report[
            "length"
        ]["words"],
        "character_count": quality_report[
            "length"
        ]["characters"],
        "estimated_pages": quality_report[
            "length"
        ]["estimated_pages"],
    }


# ==========================================================
# BACKWARD COMPATIBILITY
# ==========================================================

def generate_reply_for_metadata(
    db: Session,
    metadata_id: int,
):

    result = process_reply(
        db=db,
        metadata_id=metadata_id,
    )

    if not result:
        return None

    return result["reply"]


def process_reply_by_ocr(
    db: Session,
    ocr_result_id: int,
):

    metadata = (
        db.query(Metadata)
        .filter(
            Metadata.ocr_result_id
            == ocr_result_id
        )
        .first()
    )

    if not metadata:
        return None

    return process_reply(
        db=db,
        metadata_id=metadata.id,
    )
