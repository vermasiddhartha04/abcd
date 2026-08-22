from typing import Any, Dict, List


def build_reply_structure(
    metadata: Dict[str, Any],
    issue_analysis: Dict[str, Any],
    legal_mapping: Dict[str, Any],
    evidence_mapping: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Creates the structured outline used by the long-form
    SCN reply generator.

    The structure is dynamic:
    - More allegations -> more issue sections
    - More legal sections -> more legal discussion
    - More evidence -> more evidence sections
    - Demand data -> dedicated demand section

    This module only creates structure.
    It does not invent facts or legal conclusions.
    """

    issues = issue_analysis.get(
        "issues",
        [],
    )

    legal_sections = legal_mapping.get(
        "sections",
        [],
    )

    evidence = evidence_mapping.get(
        "available_evidence",
        [],
    )

    demand = issue_analysis.get(
        "demand",
        {},
    )

    structure: List[Dict[str, Any]] = []

    # ======================================================
    # 1. HEADER
    # ======================================================

    structure.append(
        {
            "number": "1",
            "title": "Particulars of the Show Cause Notice",
            "type": "header",
            "required": True,
        }
    )

    # ======================================================
    # 2. PRELIMINARY SUBMISSION
    # ======================================================

    structure.append(
        {
            "number": "2",
            "title": "Preliminary Submissions",
            "type": "preliminary",
            "required": True,
        }
    )

    # ======================================================
    # 3. FACTUAL BACKGROUND
    # ======================================================

    structure.append(
        {
            "number": "3",
            "title": "Brief Facts and Background",
            "type": "facts",
            "required": True,
        }
    )

    # ======================================================
    # 4. NOTICE PARTICULARS
    # ======================================================

    structure.append(
        {
            "number": "4",
            "title": "Particulars Extracted from the SCN",
            "type": "notice_particulars",
            "required": True,
        }
    )

    # ======================================================
    # 5. ALLEGATIONS
    # ======================================================

    structure.append(
        {
            "number": "5",
            "title": "Summary of Allegations",
            "type": "allegations",
            "required": True,
            "issue_count": len(issues),
        }
    )

    # ======================================================
    # 6. ISSUE-WISE REPLY
    # ======================================================

    issue_start_number = 6

    for index, issue in enumerate(
        issues,
        start=1,
    ):

        title = (
            issue.get("title")
            or f"Issue {index}"
        )

        structure.append(
            {
                "number": (
                    f"{issue_start_number}.{index}"
                ),
                "title": (
                    f"Issue-wise Reply - {title}"
                ),
                "type": "issue_response",
                "issue_number": issue.get(
                    "issue_number",
                    index,
                ),
                "required": True,
                "sections": issue.get(
                    "sections",
                    [],
                ),
            }
        )

    # If no structured issues were extracted,
    # keep one fallback section.
    if not issues:

        structure.append(
            {
                "number": "6.1",
                "title": (
                    "Response to Allegations "
                    "Identified in the SCN"
                ),
                "type": "issue_response",
                "issue_number": None,
                "required": True,
                "sections": [],
            }
        )

    # ======================================================
    # 7. FACTUAL SUBMISSIONS
    # ======================================================

    structure.append(
        {
            "number": "7",
            "title": "Detailed Factual Submissions",
            "type": "factual_submissions",
            "required": True,
        }
    )

    # ======================================================
    # 8. DOCUMENTARY EVIDENCE
    # ======================================================

    structure.append(
        {
            "number": "8",
            "title": "Documentary Evidence and Records",
            "type": "evidence",
            "required": True,
            "evidence_count": len(evidence),
        }
    )

    # ======================================================
    # 9. LEGAL SUBMISSIONS
    # ======================================================

    structure.append(
        {
            "number": "9",
            "title": "Legal Submissions",
            "type": "legal",
            "required": True,
            "section_count": len(
                legal_sections
            ),
        }
    )

    # ======================================================
    # 10. SECTION-WISE LEGAL RESPONSE
    # ======================================================

    if legal_sections:

        for index, section in enumerate(
            legal_sections,
            start=1,
        ):

            structure.append(
                {
                    "number": (
                        f"9.{index}"
                    ),
                    "title": (
                        f"Submission relating to "
                        f"{section}"
                    ),
                    "type": "legal_section",
                    "section": section,
                    "required": True,
                }
            )

    # ======================================================
    # 11. DEMAND ANALYSIS
    # ======================================================

    structure.append(
        {
            "number": "10",
            "title": "Demand and Liability Analysis",
            "type": "demand",
            "required": True,
            "tax": demand.get(
                "tax"
            ),
            "interest": demand.get(
                "interest"
            ),
            "penalty": demand.get(
                "penalty"
            ),
        }
    )

    # ======================================================
    # 12. INTEREST
    # ======================================================

    structure.append(
        {
            "number": "11",
            "title": "Interest Liability",
            "type": "interest",
            "required": (
                demand.get("interest")
                is not None
            ),
        }
    )

    # ======================================================
    # 13. PENALTY
    # ======================================================

    structure.append(
        {
            "number": "12",
            "title": "Penalty Proceedings",
            "type": "penalty",
            "required": (
                demand.get("penalty")
                is not None
            ),
        }
    )

    # ======================================================
    # 14. RUD RESPONSE
    # ======================================================

    structure.append(
        {
            "number": "13",
            "title": (
                "Response to Relied Upon Documents "
                "(RUD)"
            ),
            "type": "rud",
            "required": True,
        }
    )

    # ======================================================
    # 15. LIMITATION / JURISDICTION
    # ======================================================

    structure.append(
        {
            "number": "14",
            "title": (
                "Limitation, Jurisdiction and "
                "Procedural Submissions"
            ),
            "type": "procedural",
            "required": True,
        }
    )

    # ======================================================
    # 16. NATURAL JUSTICE
    # ======================================================

    structure.append(
        {
            "number": "15",
            "title": (
                "Principles of Natural Justice "
                "and Opportunity of Hearing"
            ),
            "type": "natural_justice",
            "required": True,
        }
    )

    # ======================================================
    # 17. WITHOUT PREJUDICE
    # ======================================================

    structure.append(
        {
            "number": "16",
            "title": "Without Prejudice Submissions",
            "type": "without_prejudice",
            "required": True,
        }
    )

    # ======================================================
    # 18. PRAYER
    # ======================================================

    structure.append(
        {
            "number": "17",
            "title": "Prayer",
            "type": "prayer",
            "required": True,
        }
    )

    # ======================================================
    # 19. PERSONAL HEARING
    # ======================================================

    structure.append(
        {
            "number": "18",
            "title": "Request for Personal Hearing",
            "type": "hearing",
            "required": True,
        }
    )

    # ======================================================
    # 20. ANNEXURES
    # ======================================================

    structure.append(
        {
            "number": "19",
            "title": "List of Annexures",
            "type": "annexures",
            "required": True,
        }
    )

    # ======================================================
    # 21. SIGNATURE
    # ======================================================

    structure.append(
        {
            "number": "20",
            "title": "Signature and Authorization",
            "type": "signature",
            "required": True,
        }
    )

    return structure


def get_required_sections(
    structure: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:

    return [
        section
        for section in structure
        if section.get(
            "required",
            False,
        )
    ]


def get_issue_sections(
    structure: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:

    return [
        section
        for section in structure
        if section.get(
            "type"
        ) == "issue_response"
    ]


def get_legal_sections(
    structure: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:

    return [
        section
        for section in structure
        if section.get(
            "type"
        ) == "legal_section"
    ]


def get_structure_statistics(
    structure: List[Dict[str, Any]],
) -> Dict[str, int]:

    return {
        "total_sections": len(
            structure
        ),
        "required_sections": len(
            get_required_sections(
                structure
            )
        ),
        "issue_sections": len(
            get_issue_sections(
                structure
            )
        ),
        "legal_sections": len(
            get_legal_sections(
                structure
            )
        ),
    }
