from sqlalchemy.orm import Session

from app.models.analysis import Analysis
from app.models.metadata import Metadata
from app.models.reply import Reply
from app.utils.reply_engine import generate_reply


def process_reply(
    db: Session,
    analysis_id: int,
    document_type: str = "SCN",
):
    # --------------------------------------------------
    # Get Analysis
    # --------------------------------------------------

    analysis = (
        db.query(Analysis)
        .filter(
            Analysis.id == analysis_id
        )
        .first()
    )

    if not analysis:
        return None

    # --------------------------------------------------
    # Existing Reply
    # --------------------------------------------------

    existing_reply = (
        db.query(Reply)
        .filter(
            Reply.analysis_id == analysis_id
        )
        .first()
    )

    if existing_reply:
        return existing_reply

    # --------------------------------------------------
    # Get Metadata
    # --------------------------------------------------

    metadata = (
        db.query(Metadata)
        .filter(
            Metadata.id == analysis.metadata_id
        )
        .first()
    )

    if not metadata:
        return None

    # --------------------------------------------------
    # Metadata
    # --------------------------------------------------

    metadata_dict = {
        "gstin": metadata.gstin,
        "pan": metadata.pan,
        "taxpayer_name": metadata.taxpayer_name,
        "notice_number": metadata.notice_number,
        "section": metadata.section,
        "financial_year": metadata.financial_year,
        "tax_period": metadata.tax_period,
        "tax_amount": metadata.tax_amount,
        "interest": metadata.interest,
        "penalty": metadata.penalty,
    }

    # --------------------------------------------------
    # Analysis
    # --------------------------------------------------

    analysis_dict = {
        "summary": analysis.summary,
        "recommendation": analysis.recommendation,
    }

    # --------------------------------------------------
    # Generate Document-specific Draft
    # --------------------------------------------------

    draft = generate_reply(
        metadata=metadata_dict,
        analysis=analysis_dict,
        document_type=document_type,
    )

    # --------------------------------------------------
    # Save
    # --------------------------------------------------

    reply = Reply(
        analysis_id=analysis.id,
        draft_reply=draft,
    )

    db.add(reply)

    db.commit()

    db.refresh(reply)

    return reply