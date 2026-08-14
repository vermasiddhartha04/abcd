from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db

from app.schemas.case import (
    CaseCreate,
    CaseResponse,
    CaseUpdate,
)

from app.services.case_service import (
    create_case,
    delete_case,
    get_all_cases,
    get_case_by_id,
    update_case,
)

router = APIRouter(
    prefix="/cases",
    tags=["Case Management"],
)


@router.post(
    "/",
    response_model=CaseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_case(
    case: CaseCreate,
    db: Session = Depends(get_db),
):
    # Temporary user_id until authentication is restored
    return create_case(
        db=db,
        case=case,
        user_id=1,
    )


@router.get(
    "/",
    response_model=list[CaseResponse],
)
def list_cases(
    db: Session = Depends(get_db),
):
    return get_all_cases(db)


@router.get(
    "/{case_id}",
    response_model=CaseResponse,
)
def get_case(
    case_id: int,
    db: Session = Depends(get_db),
):
    case = get_case_by_id(db, case_id)

    if not case:
        raise HTTPException(
            status_code=404,
            detail="Case not found",
        )

    return case


@router.put(
    "/{case_id}",
    response_model=CaseResponse,
)
def edit_case(
    case_id: int,
    case: CaseUpdate,
    db: Session = Depends(get_db),
):
    updated = update_case(
        db=db,
        case_id=case_id,
        case=case,
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Case not found",
        )

    return updated


@router.delete("/{case_id}")
def remove_case(
    case_id: int,
    db: Session = Depends(get_db),
):
    deleted = delete_case(
        db=db,
        case_id=case_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Case not found",
        )

    return {
        "message": "Case deleted successfully"
    }