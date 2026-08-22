from typing import Any, Dict, List


EVIDENCE_KEYWORDS = {
    "GST Returns": [
        "gstr",
        "return",
    ],
    "Invoices": [
        "invoice",
        "tax invoice",
    ],
    "Bank Records": [
        "bank",
        "payment",
    ],
    "Books of Account": [
        "books",
        "ledger",
        "account",
    ],
    "Reconciliation": [
        "reconciliation",
        "difference",
        "mismatch",
    ],
    "RUD": [
        "rud",
        "relied upon document",
    ],
}


def detect_evidence(text: str) -> List[Dict[str, Any]]:
    text_lower = (text or "").lower()

    evidence = []

    for label, keywords in EVIDENCE_KEYWORDS.items():

        matched = [
            keyword
            for keyword in keywords
            if keyword in text_lower
        ]

        if matched:
            evidence.append(
                {
                    "type": label,
                    "matched_keywords": matched,
                }
            )

    return evidence


def map_evidence_to_issues(
    text: str,
    issues: List[Dict[str, Any]],
) -> Dict[str, Any]:

    evidence = detect_evidence(text)

    mappings = []

    for issue in issues:
        mappings.append(
            {
                "issue_number": issue.get(
                    "issue_number"
                ),
                "evidence": evidence,
            }
        )

    return {
        "available_evidence": evidence,
        "issue_mappings": mappings,
    }
