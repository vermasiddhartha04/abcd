from collections import Counter

from sqlalchemy.orm import Session

from app.models.case import Case
from app.models.upload import Upload
from app.models.ocr_result import OCRResult
from app.models.metadata import Metadata
from app.models.analysis import Analysis
from app.models.reply import Reply


def get_dashboard_summary(db: Session):

    # ======================================================
    # EXISTING DASHBOARD METRICS
    # ======================================================

    total_cases = db.query(Case).count()

    pending_cases = (
        db.query(Case)
        .filter(Case.status == "Pending")
        .count()
    )

    closed_cases = (
        db.query(Case)
        .filter(Case.status == "Closed")
        .count()
    )

    uploads = db.query(Upload).count()

    ocr_completed = db.query(OCRResult).count()

    metadata_generated = db.query(Metadata).count()

    analysis_completed = db.query(Analysis).count()

    replies_generated = db.query(Reply).count()

    # ======================================================
    # LITIGATION INTELLIGENCE
    # ======================================================

    analyses = (
        db.query(Analysis)
        .all()
    )

    risk_distribution = Counter()

    document_type_distribution = Counter()

    demand_category_totals = Counter()

    total_proposed_demand = 0.0

    total_penalty_proposals = 0

    total_allegations = 0

    # ======================================================
    # ANALYSIS LOOP
    # ======================================================

    for analysis in analyses:

        # --------------------------------------------------
        # Risk
        # --------------------------------------------------

        risk = (
            analysis.risk_level
            or "Unknown"
        )

        risk_distribution[risk] += 1

        # --------------------------------------------------
        # Document Type
        # --------------------------------------------------

        document_type = (
            analysis.document_type
            or "UNKNOWN"
        )

        document_type_distribution[
            document_type
        ] += 1

        # --------------------------------------------------
        # Structured Demands
        # --------------------------------------------------

        demands = (
            analysis.demands
            if isinstance(
                analysis.demands,
                list,
            )
            else []
        )

        for demand in demands:

            if not isinstance(
                demand,
                dict,
            ):
                continue

            category = (
                demand.get("category")
                or "UNCLASSIFIED"
            )

            demand_category_totals[
                category
            ] += 1

            try:

                total_proposed_demand += float(
                    demand.get("amount") or 0
                )

            except (
                TypeError,
                ValueError,
            ):

                pass

        # --------------------------------------------------
        # Penalty Proposals
        # --------------------------------------------------

        penalties = (
            analysis.penalty_proposals
            if isinstance(
                analysis.penalty_proposals,
                list,
            )
            else []
        )

        total_penalty_proposals += len(
            penalties
        )

        # --------------------------------------------------
        # Allegations
        # --------------------------------------------------

        allegations = (
            analysis.allegations
            if isinstance(
                analysis.allegations,
                list,
            )
            else []
        )

        total_allegations += len(
            allegations
        )

    # ======================================================
    # FINAL DASHBOARD RESPONSE
    # ======================================================

    return {

        # Existing metrics
        "total_cases": total_cases,

        "pending_cases": pending_cases,

        "closed_cases": closed_cases,

        "uploads": uploads,

        "ocr_completed": ocr_completed,

        "metadata_generated": metadata_generated,

        "analysis_completed": analysis_completed,

        "replies_generated": replies_generated,

        # Litigation intelligence
        "risk_distribution":
            dict(
                risk_distribution
            ),

        "document_type_distribution":
            dict(
                document_type_distribution
            ),

        "total_proposed_demand":
            round(
                total_proposed_demand,
                2,
            ),

        "demand_category_totals":
            dict(
                demand_category_totals
            ),

        "total_penalty_proposals":
            total_penalty_proposals,

        "total_allegations":
            total_allegations,
    }
