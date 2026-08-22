from typing import Any, Dict, List

from app.utils.allegation_extractor import (
    extract_allegations,
    extract_issue_keywords,
)
from app.utils.demand_extractor import (
    extract_demand_summary,
)
from app.utils.table_extractor import (
    extract_tables,
)


def build_issue_analysis(
    text: str,
    metadata: Dict[str, Any],
) -> Dict[str, Any]:

    text = text or ""

    allegations = extract_allegations(text)
    keywords = extract_issue_keywords(text)
    demand = extract_demand_summary(text)
    tables = extract_tables(text)

    issues: List[Dict[str, Any]] = []

    for allegation in allegations:
        issues.append(
            {
                "issue_number": len(issues) + 1,
                "title": allegation["title"],
                "allegation": allegation["text"],
                "sections": allegation["sections"],
                "amount": None,
                "category": None,
            }
        )

    # If headings were not detected, create
    # issue categories from explicit keywords.
    if not issues:

        for keyword in keywords:
            issues.append(
                {
                    "issue_number": len(issues) + 1,
                    "title": keyword,
                    "allegation": (
                        f"SCN text contains references "
                        f"related to {keyword}."
                    ),
                    "sections": [],
                    "amount": None,
                    "category": keyword,
                }
            )

    return {
        "issues": issues,
        "issue_count": len(issues),
        "keywords": keywords,
        "demand": demand,
        "tables": tables,
        "metadata": metadata,
    }
