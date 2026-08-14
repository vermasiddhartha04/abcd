from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.analysis import AnalysisResponse
from app.services.analysis_service import process_analysis

router = APIRouter(
    prefix="/analysis",
    tags=["Analysis"],
)


@router.post(
    "/{metadata_id}",
    response_model=AnalysisResponse,
)
def generate_analysis(
    metadata_id: int,
    db: Session = Depends(get_db),
):
    analysis = process_analysis(
        db,
        metadata_id,
    )

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="Metadata not found",
        )

    return analysis