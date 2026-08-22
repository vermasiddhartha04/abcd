import re
from typing import Any, Dict, List


LEGAL_PATTERNS = {
    "Section 74": [
        r"\bsection\s+74\b",
    ],
    "Section 73": [
        r"\bsection\s+73\b",
    ],
    "Section 16": [
        r"\bsection\s+16\b",
    ],
    "Section 50": [
        r"\bsection\s+50\b",
    ],
    "Section 122": [
        r"\bsection\s+122\b",
    ],
    "Section 125": [
        r"\bsection\s+125\b",
    ],
}


def extract_legal_sections(text: str) -> List[str]:
    text = text or ""
    found = []

    for label, patterns in LEGAL_PATTERNS.items():

        for pattern in patterns:

            if re.search(
                pattern,
                text,
                re.IGNORECASE,
            ):
                if label not in found:
                    found.append(label)

                break

    return found


def build_legal_mapping(
    text: str,
    issues: List[Dict[str, Any]],
) -> Dict[str, Any]:

    sections = extract_legal_sections(text)

    mappings = []

    for issue in issues:

        issue_sections = issue.get(
            "sections",
            [],
        )

        mappings.append(
            {
                "issue_number": issue.get(
                    "issue_number"
                ),
                "sections": issue_sections,
                "general_sections": sections,
                "legal_basis_status": (
                    "EXTRACTED"
                    if issue_sections
                    else "NOT_EXTRACTED"
                ),
            }
        )

    return {
        "sections": sections,
        "issue_mappings": mappings,
    }
