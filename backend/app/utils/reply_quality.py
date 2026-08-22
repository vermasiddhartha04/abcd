import re
from typing import Any, Dict, List


# ==========================================================
# BASIC HELPERS
# ==========================================================

def _normalise(value: Any) -> str:
    return re.sub(
        r"\s+",
        " ",
        str(value or ""),
    ).strip().lower()


def _contains_value(
    reply: str,
    value: Any,
) -> bool:

    if value is None:
        return False

    value = str(value).strip()

    if not value:
        return False

    return value.lower() in reply.lower()


# ==========================================================
# REQUIRED REPLY SECTIONS
# ==========================================================

REQUIRED_HEADINGS = [
    "PRELIMINARY",
    "FACTUAL",
    "ALLEGATIONS",
    "ISSUE-WISE",
    "LEGAL",
    "EVIDENCE",
    "DEMAND",
    "PRAYER",
    "PERSONAL HEARING",
]


def check_required_sections(
    reply: str,
) -> List[Dict[str, Any]]:

    reply_lower = _normalise(
        reply
    )

    results = []

    for heading in REQUIRED_HEADINGS:

        found = heading.lower() in reply_lower

        results.append(
            {
                "section": heading,
                "status": (
                    "FOUND"
                    if found
                    else "MISSING"
                ),
            }
        )

    return results


# ==========================================================
# METADATA CHECK
# ==========================================================

def check_metadata(
    reply: str,
    metadata: Dict[str, Any],
) -> List[Dict[str, Any]]:

    fields = [
        "taxpayer_name",
        "gstin",
        "notice_number",
        "financial_year",
        "tax_period",
    ]

    results = []

    for field in fields:

        value = metadata.get(
            field
        )

        if not value:

            results.append(
                {
                    "field": field,
                    "status": "SOURCE_NOT_AVAILABLE",
                    "value": None,
                }
            )

            continue

        found = _contains_value(
            reply,
            value,
        )

        results.append(
            {
                "field": field,
                "status": (
                    "FOUND"
                    if found
                    else "MISSING"
                ),
                "value": value,
            }
        )

    return results


# ==========================================================
# DEMAND CHECK
# ==========================================================

def check_demand(
    reply: str,
    demand: Dict[str, Any],
) -> List[Dict[str, Any]]:

    results = []

    fields = [
        "tax",
        "interest",
        "penalty",
    ]

    for field in fields:

        value = demand.get(
            field
        )

        if value is None:

            results.append(
                {
                    "field": field,
                    "status": "SOURCE_NOT_AVAILABLE",
                    "value": None,
                }
            )

            continue

        try:
            numeric = float(
                value
            )

            formatted = (
                f"{numeric:,.2f}"
            )

        except (
            TypeError,
            ValueError,
        ):

            formatted = str(
                value
            )

        found = (
            formatted in reply
            or str(value) in reply
        )

        results.append(
            {
                "field": field,
                "status": (
                    "FOUND"
                    if found
                    else "MISSING"
                ),
                "value": value,
            }
        )

    return results


# ==========================================================
# ISSUE CHECK
# ==========================================================

def check_issues(
    reply: str,
    issues: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:

    results = []

    for index, issue in enumerate(
        issues,
        start=1,
    ):

        title = issue.get(
            "title"
        )

        allegation = issue.get(
            "allegation"
        )

        title_found = (
            _contains_value(
                reply,
                title,
            )
            if title
            else False
        )

        # We don't require the complete allegation
        # because OCR text can be very long.
        allegation_words = re.findall(
            r"\b[A-Za-z]{5,}\b",
            str(allegation or ""),
        )

        sample_words = allegation_words[:8]

        matched_words = [
            word
            for word in sample_words
            if word.lower()
            in reply.lower()
        ]

        results.append(
            {
                "issue_number": issue.get(
                    "issue_number",
                    index,
                ),
                "title_found": title_found,
                "allegation_reference": (
                    len(matched_words) >= 2
                ),
                "matched_words": matched_words,
                "status": (
                    "COVERED"
                    if (
                        title_found
                        or len(matched_words) >= 2
                    )
                    else "REVIEW_REQUIRED"
                ),
            }
        )

    return results


# ==========================================================
# LEGAL SECTION CHECK
# ==========================================================

def check_legal_sections(
    reply: str,
    sections: List[str],
) -> List[Dict[str, Any]]:

    results = []

    for section in sections:

        found = _contains_value(
            reply,
            section,
        )

        results.append(
            {
                "section": section,
                "status": (
                    "FOUND"
                    if found
                    else "MISSING"
                ),
            }
        )

    return results


# ==========================================================
# REPLY LENGTH
# ==========================================================

def calculate_length(
    reply: str,
) -> Dict[str, int]:

    words = re.findall(
        r"\S+",
        reply or "",
    )

    characters = len(
        reply or ""
    )

    return {
        "words": len(words),
        "characters": characters,
        "estimated_pages": max(
            1,
            round(
                len(words) / 450
            ),
        ),
    }


# ==========================================================
# GENERIC QUALITY CHECKS
# ==========================================================

def check_quality_flags(
    reply: str,
) -> List[Dict[str, Any]]:

    reply_lower = _normalise(
        reply
    )

    flags = []

    generic_phrases = [
        "review the scn carefully",
        "prepare factual and legally supported submissions",
        "the taxpayer respectfully submits",
    ]

    generic_count = sum(
        1
        for phrase in generic_phrases
        if phrase in reply_lower
    )

    if generic_count >= 3:

        flags.append(
            {
                "type": "GENERIC_LANGUAGE",
                "severity": "MEDIUM",
                "message": (
                    "Reply contains multiple generic "
                    "submission phrases. Issue-specific "
                    "factual drafting should be reviewed."
                ),
            }
        )

    if len(
        re.findall(
            r"\S+",
            reply or "",
        )
    ) < 500:

        flags.append(
            {
                "type": "SHORT_REPLY",
                "severity": "MEDIUM",
                "message": (
                    "Generated reply is relatively short "
                    "for a detailed SCN response."
                ),
            }
        )

    if "prayer" not in reply_lower:

        flags.append(
            {
                "type": "PRAYER_MISSING",
                "severity": "HIGH",
                "message": (
                    "Prayer section was not detected."
                ),
            }
        )

    if (
        "personal hearing"
        not in reply_lower
    ):

        flags.append(
            {
                "type": "HEARING_REQUEST_MISSING",
                "severity": "MEDIUM",
                "message": (
                    "Personal hearing request was not detected."
                ),
            }
        )

    return flags


# ==========================================================
# FINAL QUALITY REPORT
# ==========================================================

def evaluate_reply_quality(
    reply: str,
    metadata: Dict[str, Any],
    issue_analysis: Dict[str, Any],
    legal_mapping: Dict[str, Any],
    evidence_mapping: Dict[str, Any],
) -> Dict[str, Any]:

    reply = reply or ""

    issues = issue_analysis.get(
        "issues",
        [],
    )

    demand = issue_analysis.get(
        "demand",
        {},
    )

    legal_sections = legal_mapping.get(
        "sections",
        [],
    )

    evidence = evidence_mapping.get(
        "available_evidence",
        [],
    )

    section_results = (
        check_required_sections(
            reply
        )
    )

    metadata_results = (
        check_metadata(
            reply,
            metadata,
        )
    )

    demand_results = (
        check_demand(
            reply,
            demand,
        )
    )

    issue_results = (
        check_issues(
            reply,
            issues,
        )
    )

    legal_results = (
        check_legal_sections(
            reply,
            legal_sections,
        )
    )

    length = calculate_length(
        reply
    )

    flags = check_quality_flags(
        reply
    )

    # ------------------------------------------------------
    # SCORE
    # ------------------------------------------------------

    score = 100

    missing_sections = sum(
        1
        for item in section_results
        if item["status"] == "MISSING"
    )

    missing_metadata = sum(
        1
        for item in metadata_results
        if item["status"] == "MISSING"
    )

    missing_demand = sum(
        1
        for item in demand_results
        if item["status"] == "MISSING"
    )

    missing_issues = sum(
        1
        for item in issue_results
        if item["status"] == "REVIEW_REQUIRED"
    )

    missing_legal = sum(
        1
        for item in legal_results
        if item["status"] == "MISSING"
    )

    score -= (
        missing_sections * 5
    )

    score -= (
        missing_metadata * 3
    )

    score -= (
        missing_demand * 4
    )

    score -= (
        missing_issues * 5
    )

    score -= (
        missing_legal * 4
    )

    for flag in flags:

        if flag["severity"] == "HIGH":
            score -= 10

        elif flag["severity"] == "MEDIUM":
            score -= 5

        else:
            score -= 2

    score = max(
        0,
        min(
            100,
            score,
        ),
    )

    if score >= 85:
        status = "GOOD"

    elif score >= 70:
        status = "REVIEW"

    else:
        status = "NEEDS_IMPROVEMENT"

    return {
        "score": score,
        "status": status,
        "length": length,
        "required_sections": section_results,
        "metadata_checks": metadata_results,
        "demand_checks": demand_results,
        "issue_checks": issue_results,
        "legal_section_checks": legal_results,
        "evidence_count": len(
            evidence
        ),
        "quality_flags": flags,
    }


# ==========================================================
# SIMPLE BOOLEAN HELPER
# ==========================================================

def is_reply_ready(
    quality_report: Dict[str, Any],
) -> bool:

    return (
        quality_report.get(
            "status"
        ) == "GOOD"
        and quality_report.get(
            "score",
            0,
        ) >= 85
    )
