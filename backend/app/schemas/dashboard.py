from typing import Dict

from pydantic import BaseModel


class DashboardSummary(BaseModel):

    # ======================================================
    # EXISTING METRICS
    # ======================================================

    total_cases: int

    pending_cases: int

    closed_cases: int

    uploads: int

    ocr_completed: int

    metadata_generated: int

    analysis_completed: int

    replies_generated: int

    # ======================================================
    # LITIGATION INTELLIGENCE
    # ======================================================

    risk_distribution: Dict[str, int]

    document_type_distribution: Dict[str, int]

    total_proposed_demand: float

    demand_category_totals: Dict[str, int]

    total_penalty_proposals: int

    total_allegations: int
