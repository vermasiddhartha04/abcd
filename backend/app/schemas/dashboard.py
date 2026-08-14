from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_cases: int
    pending_cases: int
    closed_cases: int

    uploads: int

    ocr_completed: int

    metadata_generated: int

    analysis_completed: int

    replies_generated: int