from sqlalchemy.orm import Session

from app.models.case import Case
from app.models.upload import Upload
from app.models.ocr_result import OCRResult
from app.models.metadata import Metadata
from app.models.analysis import Analysis
from app.models.reply import Reply


def get_dashboard_summary(db: Session):
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

    return {
        "total_cases": total_cases,
        "pending_cases": pending_cases,
        "closed_cases": closed_cases,
        "uploads": uploads,
        "ocr_completed": ocr_completed,
        "metadata_generated": metadata_generated,
        "analysis_completed": analysis_completed,
        "replies_generated": replies_generated,
    }