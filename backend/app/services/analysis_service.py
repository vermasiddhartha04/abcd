from sqlalchemy.orm import Session

from app.models.analysis import Analysis
from app.models.metadata import Metadata
from app.models.ocr_result import OCRResult

from app.utils.analysis_engine import analyze_notice

from app.utils.demand_extractor import (
    extract_demand_summary,
)

from app.utils.allegation_extractor import (
    extract_allegations,
)


def process_analysis(
    db: Session,
    metadata_id: int,
):
    """
    Process GST litigation analysis.

    Supported document types:

    DRC-01A
    SCN
    SCN_REPLY
    OIO
    APPEAL
    OIA
    UNKNOWN

    The analysis engine determines:

    - Document type
    - Current stage
    - Next stage
    - Required action
    - Risk level
    - GST sections
    - Issue category
    - Issue
    - Summary
    - Recommendation
    """

    # ==========================================================
    # 1. FIND METADATA
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
    # 2. FIND OCR RESULT
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
    # 3. COMPLETE METADATA
    # ==========================================================

    # ==========================================================
    # 3A. EXTRACT STRUCTURED LITIGATION DATA
    # ==========================================================

    text = (
        ocr_result.extracted_text
        or ""
    )

    demand_summary = (
        extract_demand_summary(
            text
        )
    )

    allegations = (
        extract_allegations(
            text
        )
    )

    # ==========================================================
    # 3B. COMPLETE METADATA
    # ==========================================================

    # ==========================================================
    # 3A. EXTRACT STRUCTURED LITIGATION DATA
    # ==========================================================

    text = (
        ocr_result.extracted_text
        or ""
    )

    demand_summary = (
        extract_demand_summary(
            text
        )
    )

    allegations = (
        extract_allegations(
            text
        )
    )

    # ==========================================================
    # 3B. COMPLETE ANALYSIS METADATA
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

        # Supplier / Vendor
        "vendor":
            metadata.vendor,

        "vendor_gstin":
            metadata.vendor_gstin,

        # Demand extraction
        "demands":
            demand_summary.get(
                "items",
                [],
            ),

        "tax_total":
            demand_summary.get(
                "tax_total"
            ),

        "interest_total":
            demand_summary.get(
                "interest_total"
            ),

        "penalty_total":
            demand_summary.get(
                "penalty_total"
            ),

        "total_demand":
            demand_summary.get(
                "total_demand"
            ),

        # Penalty proposals
        "penalty_proposals":
            demand_summary.get(
                "penalty_proposals",
                [],
            ),

        # Allegations
        "allegations":
            allegations,
    }

    # ==========================================================
    # 4. RUN ANALYSIS ENGINE
    # ==========================================================

    result = analyze_notice(
        text=ocr_result.extracted_text or "",
        metadata=metadata_dict,
    )

    # ==========================================================
    # 5. FIND EXISTING ANALYSIS
    # ==========================================================

    analysis = (
        db.query(Analysis)
        .filter(
            Analysis.metadata_id == metadata.id
        )
        .first()
    )

    # ==========================================================
    # 6. VALUES FROM ANALYSIS ENGINE
    # ==========================================================

    document_type = result.get(
        "document_type",
        "UNKNOWN",
    )

    summary = result.get(
        "summary",
    )

    risk_level = result.get(
        "risk_level",
        "Low",
    )

    reply_required = result.get(
        "reply_required",
        False,
    )

    recommendation = result.get(
        "recommendation",
    )

    # ==========================================================
    # 7. UPDATE EXISTING ANALYSIS
    # ==========================================================

    if analysis:

        analysis.document_type = (
            document_type
        )

        analysis.summary = (
            summary
        )

        analysis.risk_level = (
            risk_level
        )

        analysis.reply_required = (
            reply_required
        )

        analysis.recommendation = (
            recommendation
        )

        analysis.demands = (
            demand_summary.get(
                "items",
                [],
            )
        )

        analysis.penalty_proposals = (
            demand_summary.get(
                "penalty_proposals",
                [],
            )
        )

        analysis.allegations = (
            allegations
        )

    # ==========================================================
    # 8. CREATE NEW ANALYSIS
    # ==========================================================

    else:

        analysis = Analysis(

            metadata_id=metadata.id,

            document_type=(
                document_type
            ),

            summary=(
                summary
            ),

            risk_level=(
                risk_level
            ),

            reply_required=(
                reply_required
            ),

            recommendation=(
                recommendation
            ),

            demands=(
                demand_summary.get(
                    "items",
                    [],
                )
            ),

            penalty_proposals=(
                demand_summary.get(
                    "penalty_proposals",
                    [],
                )
            ),

            allegations=(
                allegations
            ),
        )

        db.add(analysis)

    # ==========================================================
    # 9. SAVE
    # ==========================================================

    db.commit()

    db.refresh(analysis)

    return analysis
