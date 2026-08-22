import re
from typing import Any, Dict, List


def validate_reply(
    reply: str,
    metadata: Dict[str, Any],
) -> Dict[str, Any]:

    reply = reply or ""

    checks: List[Dict[str, Any]] = []

    fields = {
        "gstin": metadata.get("gstin"),
        "taxpayer_name": metadata.get("taxpayer_name"),
        "notice_number": metadata.get("notice_number"),
        "financial_year": metadata.get("financial_year"),
    }

    for field, value in fields.items():

        if not value:
            checks.append(
                {
                    "field": field,
                    "status": "MISSING_SOURCE_DATA",
                }
            )
            continue

        checks.append(
            {
                "field": field,
                "status": (
                    "FOUND_IN_REPLY"
                    if str(value).lower()
                    in reply.lower()
                    else "NOT_FOUND_IN_REPLY"
                ),
            }
        )

    amount = metadata.get("tax_amount")

    if amount is not None:

        formatted = f"{float(amount):,.2f}"

        checks.append(
            {
                "field": "tax_amount",
                "status": (
                    "FOUND_IN_REPLY"
                    if formatted in reply
                    else "NOT_FOUND_IN_REPLY"
                ),
            }
        )

    return {
        "valid": not any(
            item["status"] == "NOT_FOUND_IN_REPLY"
            for item in checks
        ),
        "checks": checks,
        "character_count": len(reply),
        "word_count": len(
            re.findall(
                r"\S+",
                reply,
            )
        ),
    }
