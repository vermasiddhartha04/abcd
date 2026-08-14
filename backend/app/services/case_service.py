from sqlalchemy.orm import Session

from app.models.case import Case
from app.schemas.case import CaseCreate, CaseUpdate


def create_case(
    db: Session,
    case: CaseCreate,
    user_id: int,
):
    db_case = Case(
        case_no=case.case_no,
        gstin=case.gstin,
        taxpayer_name=case.taxpayer_name,
        notice_type=case.notice_type,
        financial_year=case.financial_year,
        status=case.status,
        uploaded_by=user_id,
    )

    db.add(db_case)
    db.commit()
    db.refresh(db_case)

    return db_case


def get_all_cases(db: Session):
    return db.query(Case).all()


def get_case_by_id(
    db: Session,
    case_id: int,
):
    return (
        db.query(Case)
        .filter(Case.id == case_id)
        .first()
    )


def update_case(
    db: Session,
    case_id: int,
    case: CaseUpdate,
):
    db_case = get_case_by_id(db, case_id)

    if not db_case:
        return None

    update_data = case.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_case, key, value)

    db.commit()
    db.refresh(db_case)

    return db_case


def delete_case(
    db: Session,
    case_id: int,
):
    db_case = get_case_by_id(db, case_id)

    if not db_case:
        return False

    db.delete(db_case)
    db.commit()

    return True