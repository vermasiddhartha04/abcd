from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.reply import ReplyResponse
from app.services.reply_service import process_reply

router = APIRouter(
    prefix="/reply",
    tags=["Reply"],
)


@router.post(
    "/{analysis_id}",
    response_model=ReplyResponse,
)
def generate_reply_api(
    analysis_id: int,
    db: Session = Depends(get_db),
):
    reply = process_reply(
        db,
        analysis_id,
    )

    if not reply:
        raise HTTPException(
            status_code=404,
            detail="Analysis not found",
        )

    return reply