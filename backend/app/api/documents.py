from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def documents_home():
    return {
        "module": "Documents",
        "status": "working"
    }