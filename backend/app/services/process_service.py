import re

from sqlalchemy.orm import Session

from app.models.upload import Upload

from app.services.ocr_service import process_ocr
from app.services.metadata_service import process_metadata
from app.services.analysis_service import process_analysis
from app.services.reply_service import process_reply

from app.utils.analysis_engine import analyze_notice


# ==========================================================
# SECTION NORMALIZER
# ==========================================================

def normalize_sections(value):

    if not value:
        return []

    if isinstance(value, str):

        matches = re.findall(
            r"Section\s+(?:Section\s+)*"
            r"(\d+[A-Z]?(?:\([0-9A-Z]+\))?)",
            value,
            re.IGNORECASE,
        )

        sections = []

        for number in matches:

            section = f"Section {number}"

            if section not in sections:
                sections.append(section)

        if sections:
            return sections

        return [
            item.strip()
            for item in value.split(",")
            if item.strip()
        ]

    if isinstance(value, list):

        sections = []

        for item in value:

            if not item:
                continue

            item = str(item).strip()

            matches = re.findall(
                r"Section\s+(?:Section\s+)*"
                r"(\d+[A-Z]?(?:\([0-9A-Z]+\))?)",
                item,
                re.IGNORECASE,
            )

            if matches:

                for number in matches:

                    section = f"Section {number}"

                    if section not in sections:
                        sections.append(section)

            elif item not in sections:

                sections.append(item)

        return sections

    return []


# ==========================================================
# DOCUMENT TYPE NORMALIZER
# ==========================================================

def normalize_document_type(value):

    if not value:
        return "UNKNOWN"

    value = (
        str(value)
        .upper()
        .strip()
    )

    value = value.replace("-", "_")
    value = value.replace(" ", "_")

    return value


# ==========================================================
# PROCESS DOCUMENT
# ==========================================================

def process_document(
    db: Session,
    upload_id: int,
):

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
    # 5. COMPLETE METADATA
    # ==========================================================

    metadata_dict = {

        "gstin":
            metadata.gstin,

        "pan":
            metadata.pan,

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
    }

    # ==========================================================
    # 6. WORKFLOW ANALYSIS
    # ==========================================================

    workflow_analysis = analyze_notice(
        text=ocr_result.extracted_text,
        metadata=metadata_dict,
    )

    raw_document_type = (
        workflow_analysis.get(
            "document_type"
        )
        or analysis.document_type
        or metadata.document_type
        or "UNKNOWN"
    )

    document_type = normalize_document_type(
        raw_document_type
    )

    # Frontend display name
    if document_type == "DRC_01A":
        display_document_type = "DRC-01A"
    else:
        display_document_type = document_type

    # ==========================================================
    # 7. RISK LEVEL
    # ==========================================================

    risk_level = (
        workflow_analysis.get(
            "risk_level"
        )
        or analysis.risk_level
        or "Medium"
    )

    # ==========================================================
    # 8. CURRENT STAGE
    # ==========================================================

    current_stage = (
        workflow_analysis.get(
            "current_stage"
        )
    )

    if not current_stage:

        if document_type in {
            "DRC_01A",
            "PRE_SCN",
        }:

            current_stage = "PRE_SCN"

        elif document_type == "SCN":

            current_stage = "SCN"

        elif document_type == "SCN_REPLY":

            current_stage = "SCN_REPLY"

        elif document_type == "OIO":

            current_stage = "OIO"

        elif document_type == "APPEAL":

            current_stage = "APPEAL"

        elif document_type == "OIA":

            current_stage = "OIA"

        else:

            current_stage = document_type

    current_stage = normalize_document_type(
        current_stage
    )

    # ==========================================================
    # 9. NEXT STAGE
    # ==========================================================

    next_stage = (
        workflow_analysis.get(
            "next_stage"
        )
    )

    if next_stage:

        next_stage = normalize_document_type(
            next_stage
        )

    stage_map = {

        "PRE_SCN":
            "SCN",

        "DRC_01A":
            "SCN",

        "SCN":
            "SCN_REPLY",

        "SCN_REPLY":
            "OIO",

        "OIO":
            "APPEAL",

        "APPEAL":
            "OIA",

        "OIA":
            "FINAL",

        "FINAL":
            "FINAL",
    }

    if not next_stage:

        next_stage = stage_map.get(
            current_stage
        )

    # ==========================================================
    # 10. REPLY REQUIRED
    # ==========================================================

    reply_required = workflow_analysis.get(
        "reply_required"
    )

    if reply_required is None:

        reply_required = (
            current_stage
            in {
                "PRE_SCN",
                "SCN",
                "OIO",
                "APPEAL",
                "OIA",
            }
        )

    # ==========================================================
    # 11. APPEAL REQUIRED
    # ==========================================================

    appeal_required = workflow_analysis.get(
        "appeal_required"
    )

    if appeal_required is None:

        appeal_required = (
            current_stage == "OIO"
        )

    # ==========================================================
    # 12. ACTION TYPE
    # ==========================================================

    action_type = (
        workflow_analysis.get(
            "action_type"
        )
    )

    if not action_type:

        action_type_map = {

            "PRE_SCN":
                "PRE_SCN_RESPONSE",

            "SCN":
                "SCN_REPLY",

            "SCN_REPLY":
                "OIO",

            "OIO":
                "APPEAL",

            "APPEAL":
                "OIA",

            "OIA":
                "FINAL",
        }

        action_type = (
            action_type_map.get(
                current_stage
            )
        )

    # ==========================================================
    # 13. ACTION LABEL
    # ==========================================================

    action_label = (
        workflow_analysis.get(
            "action_label"
        )
    )

    if not action_label:

        action_label_map = {

            "PRE_SCN":
                "Submit response or pay liability within 15 days",

            "SCN":
                "Prepare and submit SCN Reply",

            "SCN_REPLY":
                "Review and submit SCN Reply",

            "OIO":
                "File Appeal",

            "APPEAL":
                "Review Appeal",

            "OIA":
                "Final Review",
        }

        action_label = (
            action_label_map.get(
                current_stage
            )
        )

    # ==========================================================
    # 14. REPLY GENERATION
    # ==========================================================

    reply = None

    reply_result = None

    reply_request_type = None

    if current_stage == "PRE_SCN":

        reply_request_type = "PRE_SCN"

    elif current_stage == "SCN":

        reply_request_type = "SCN"

    elif current_stage == "SCN_REPLY":

        reply_request_type = "SCN_REPLY"

    elif current_stage == "OIO":

        reply_request_type = "OIO"

    elif current_stage == "APPEAL":

        reply_request_type = "APPEAL"

    elif current_stage == "OIA":

        reply_request_type = "OIA"

    # ----------------------------------------------------------
    # New reply pipeline
    #
    # Metadata
    #   -> OCR
    #   -> Issue Analysis
    #   -> Legal Mapping
    #   -> Evidence Mapping
    #   -> Reply Engine
    #   -> Quality Check
    #   -> DOCX
    # ----------------------------------------------------------

    if reply_request_type:

        if metadata:

            reply_result = process_reply(
                db=db,
                metadata_id=metadata.id,
            )

            if reply_result:

                reply = reply_result.get(
                    "reply"
                )

    # ==========================================================
    # 15. SECTIONS
    # ==========================================================

    sections = normalize_sections(
        workflow_analysis.get(
            "sections",
            [],
        )
    )

    if not sections:

        sections = normalize_sections(
            metadata.section
        )

    # ==========================================================
    # 16. DOCUMENT RESPONSE
    # ==========================================================

    document_response = {

        "document_type":
            display_document_type,

        "current_stage":
            current_stage,

        "next_stage":
            next_stage,

        "action_type":
            action_type,

        "action_label":
            action_label,
    }

    # ==========================================================
    # 17. METADATA RESPONSE
    # ==========================================================

    metadata_response = {

        "gstin":
            metadata.gstin,

        "pan":
            metadata.pan,

        "taxpayer_name":
            metadata.taxpayer_name,

        "notice_number":
            metadata.notice_number,

        "document_type":
            display_document_type,

        "section":
            metadata.section,

        "financial_year":
            metadata.financial_year,

        "tax_period":
            metadata.tax_period,

        "tax_amount":
            (
                str(metadata.tax_amount)
                if metadata.tax_amount is not None
                else None
            ),

        "interest":
            (
                str(metadata.interest)
                if metadata.interest is not None
                else None
            ),

        "penalty":
            (
                str(metadata.penalty)
                if metadata.penalty is not None
                else None
            ),
    }

    # ==========================================================
    # 18. ANALYSIS RESPONSE
    # ==========================================================

    analysis_response = {

        "document_type":
            display_document_type,

        "summary":
            analysis.summary,

        "risk_level":
            risk_level,

        "reply_required":
            reply_required,

        "appeal_required":
            appeal_required,

        "recommendation":
            analysis.recommendation,

        "sections":
            sections,

        "action_type":
            action_type,

        "action_label":
            action_label,

        "current_stage":
            current_stage,

        "next_stage":
            next_stage,
    }

    # ==========================================================
    # 19. REPLY RESPONSE
    # ==========================================================

    reply_response = None

    if reply:

        # IMPORTANT:
        # Reply model only contains:
        # id
        # analysis_id
        # draft_reply
        #
        # It does NOT contain document_type.

        if current_stage == "PRE_SCN":

            reply_document_type = "PRE_SCN_REPLY"

        elif current_stage == "SCN":

            reply_document_type = "SCN_REPLY"

        else:

            reply_document_type = current_stage

        reply_response = {

            "id":
                reply.id,

            "document_type":
                reply_document_type,

            "draft_reply":
                reply.draft_reply,
        }

    # ==========================================================
    # 20. LITIGATION WORKFLOW
    # ==========================================================

    litigation = {

        "current_stage":
            current_stage,

        "next_stage":
            next_stage,

        "action_required":
            bool(action_type),

        "action_type":
            action_type,

        "action_label":
            action_label,

        "reply_required":
            reply_required,

        "appeal_required":
            appeal_required,

        "workflow": [

            "PRE_SCN",

            "SCN",

            "SCN_REPLY",

            "OIO",

            "APPEAL",

            "OIA",

            "FINAL",
        ],
    }

    # ==========================================================
    # 21. FINAL RESPONSE
    # ==========================================================

    return {

        "success":
            True,

        "upload_id":
            upload.id,

        "ocr_result_id":
            ocr_result.id,

        "metadata_id":
            metadata.id,

        "analysis_id":
            analysis.id,

        "reply_id":
            (
                reply.id
                if reply
                else None
            ),

        "document":
            document_response,

        "metadata":
            metadata_response,

        "analysis":
            analysis_response,

        "reply":
            reply_response,

        "litigation":
            litigation,
    }
