import re
from typing import Any, Dict, List

from app.utils.issue_engine import build_issue_analysis
from app.utils.legal_mapper import build_legal_mapping
from app.utils.evidence_mapper import map_evidence_to_issues
from app.utils.reply_validator import validate_reply


# ==========================================================
# HELPERS
# ==========================================================

def _clean(value: Any, default: str = "") -> str:
    if value is None:
        return default

    return re.sub(
        r"\s+",
        " ",
        str(value),
    ).strip()


def _money(value: Any) -> str:
    if value is None:
        return "Not available"

    try:
        return f"₹{float(value):,.2f}"
    except (TypeError, ValueError):
        return str(value)


def _metadata_value(
    metadata: Dict[str, Any],
    key: str,
    fallback: str = "Not available",
) -> str:

    value = metadata.get(key)

    if value is None:
        return fallback

    value = _clean(value)

    return value if value else fallback


# ==========================================================
# STRUCTURED LITIGATION DATA
# ==========================================================

def _structured_items(
    metadata: Dict[str, Any],
    key: str,
) -> List[Dict[str, Any]]:

    value = metadata.get(key)

    if not isinstance(value, list):
        return []

    return [
        item
        for item in value
        if isinstance(item, dict)
    ]


def build_structured_allegations(
    metadata: Dict[str, Any],
) -> str:

    allegations = _structured_items(
        metadata,
        "allegations",
    )

    if not allegations:
        return (
            "No structured allegations were "
            "available from the analysis."
        )

    lines = [
        "The following allegations were "
        "structured from the source notice:"
    ]

    for item in allegations:

        number = _clean(
            item.get("number"),
            "Not numbered",
        )

        category = _clean(
            item.get("category"),
            "UNCLASSIFIED",
        )

        lines.append(
            f"- {number}: {category}"
        )

    return "\n".join(lines)


def build_structured_demands(
    metadata: Dict[str, Any],
) -> str:

    demands = _structured_items(
        metadata,
        "demands",
    )

    if not demands:
        return (
            "No structured demand items were "
            "available from the analysis."
        )

    lines = [
        "The following demand components were "
        "identified from the source notice:"
    ]

    for item in demands:

        number = _clean(
            item.get("demand_number"),
            "Not numbered",
        )

        category = _clean(
            item.get("category"),
            "UNCLASSIFIED",
        )

        amount = _money(
            item.get("amount")
        )

        lines.append(
            f"- Demand {number}: "
            f"{category} — {amount}"
        )

    return "\n".join(lines)


def build_structured_penalties(
    metadata: Dict[str, Any],
) -> str:

    penalties = _structured_items(
        metadata,
        "penalty_proposals",
    )

    if not penalties:
        return (
            "No structured penalty proposals "
            "were available from the analysis."
        )

    lines = [
        "The following penalty proposals were "
        "identified from the source notice:"
    ]

    for item in penalties:

        number = _clean(
            item.get("penalty_number"),
            "Not numbered",
        )

        linked = _clean(
            item.get("linked_demand_number"),
            "Not linked",
        )

        category = _clean(
            item.get("category"),
            "UNCLASSIFIED",
        )

        section = _clean(
            item.get("section"),
            "Section not identified",
        )

        lines.append(
            f"- Penalty {number}: "
            f"linked to demand {linked}; "
            f"{category}; {section}"
        )

    return "\n".join(lines)


# ==========================================================
# SOURCE SUMMARY
# ==========================================================

def build_source_summary(
    metadata: Dict[str, Any],
) -> str:

    taxpayer = _metadata_value(
        metadata,
        "taxpayer_name",
        "the Noticee",
    )

    gstin = _metadata_value(
        metadata,
        "gstin",
        "not available",
    )

    notice_number = _metadata_value(
        metadata,
        "notice_number",
        "not available",
    )

    financial_year = _metadata_value(
        metadata,
        "financial_year",
        "not available",
    )

    tax_period = _metadata_value(
        metadata,
        "tax_period",
        "not available",
    )

    tax_amount = _money(
        metadata.get("tax_amount")
    )

    interest = _money(
        metadata.get("interest")
    )

    penalty = _money(
        metadata.get("penalty")
    )

    return (
        f"The Show Cause Notice concerns {taxpayer}. "
        f"The GSTIN identified from the source document is "
        f"{gstin}. The notice number is {notice_number}. "
        f"The financial year/period identified in the source "
        f"document is {financial_year}, with tax period "
        f"{tax_period}. The extracted tax amount is "
        f"{tax_amount}; interest is {interest}; and penalty "
        f"is {penalty}."
    )


# ==========================================================
# ISSUE RESPONSE
# ==========================================================

def build_issue_response(
    issue: Dict[str, Any],
) -> str:

    number = issue.get(
        "issue_number",
        1,
    )

    title = _clean(
        issue.get("title"),
        "Issue identified in the SCN",
    )

    allegation = _clean(
        issue.get("allegation"),
        "The SCN contains an allegation requiring examination.",
    )

    sections = issue.get(
        "sections",
        [],
    )

    if sections:
        section_text = ", ".join(
            str(section)
            for section in sections
        )
    else:
        section_text = (
            "No specific section was directly mapped "
            "to this issue by the extractor."
        )

    amount = issue.get(
        "amount"
    )

    amount_text = (
        _money(amount)
        if amount is not None
        else "Not separately extracted"
    )

    return (
        f"{number}. {title}\n\n"
        f"Allegation identified from the SCN:\n"
        f"{allegation}\n\n"
        f"Relevant extracted GST sections:\n"
        f"{section_text}\n\n"
        f"Amount linked directly to this issue:\n"
        f"{amount_text}\n\n"
        f"Reply / submission:\n"
        f"The Noticee respectfully submits that the allegation "
        f"should be examined with reference to the complete "
        f"transaction records, GST returns, invoices, books of "
        f"account, reconciliations and other supporting records "
        f"available for the relevant period. The allegation is "
        f"denied to the extent that it is inconsistent with the "
        f"actual records and applicable law. The Noticee "
        f"reserves the right to provide issue-specific documents "
        f"and detailed submissions in support of the above."
    )


# ==========================================================
# LEGAL SUBMISSIONS
# ==========================================================

def build_legal_submissions(
    legal_mapping: Dict[str, Any],
) -> str:

    sections = legal_mapping.get(
        "sections",
        [],
    )

    if sections:
        section_text = ", ".join(
            sections
        )
    else:
        section_text = (
            "No general GST sections were extracted."
        )

    return (
        "The Noticee respectfully submits that the allegations "
        "contained in the Show Cause Notice must be examined "
        "strictly with reference to the facts stated in the "
        "notice, the documents relied upon by the department, "
        "the records maintained by the Noticee and the specific "
        "statutory provisions applicable to each allegation.\n\n"
        "The following sections were identified from the source "
        "document:\n"
        f"{section_text}\n\n"
        "The Noticee does not admit any allegation merely because "
        "a statutory provision has been cited in the Show Cause "
        "Notice. Each allegation, factual foundation and proposed "
        "liability should be independently established from the "
        "relevant records and applicable provisions."
    )


# ==========================================================
# EVIDENCE SUBMISSIONS
# ==========================================================

def build_evidence_submissions(
    evidence_mapping: Dict[str, Any],
) -> str:

    evidence = evidence_mapping.get(
        "available_evidence",
        [],
    )

    if not evidence:

        return (
            "The source text did not provide sufficient evidence "
            "categories for a specific mapping. The Noticee may "
            "submit relevant GST returns, invoices, books of "
            "account, payment records, reconciliation statements "
            "and other documents wherever applicable."
        )

    lines = []

    for item in evidence:

        evidence_type = _clean(
            item.get("type"),
            "Supporting record",
        )

        keywords = item.get(
            "matched_keywords",
            [],
        )

        keyword_text = (
            ", ".join(keywords)
            if keywords
            else "source reference"
        )

        lines.append(
            f"- {evidence_type}: "
            f"identified through {keyword_text}."
        )

    return (
        "The following evidence categories were identified "
        "from the source document:\n\n"
        + "\n".join(lines)
        + "\n\n"
        "The Noticee submits that the relevant original records "
        "and supporting documents should be considered while "
        "determining the correctness of the allegations and "
        "proposed liability."
    )


# ==========================================================
# PRAYER
# ==========================================================

def build_prayer() -> str:

    return (
        "PRAYER\n\n"
        "In view of the facts, records, documents and submissions "
        "that may be furnished in support of the Noticee's case, "
        "it is respectfully prayed that the allegations and "
        "proposed demand contained in the Show Cause Notice be "
        "examined objectively and that the proceedings be "
        "dropped to the extent the allegations are not "
        "established in accordance with law.\n\n"
        "The Noticee further requests that an opportunity of "
        "personal hearing be granted before any adverse order "
        "is passed, in accordance with applicable law."
    )


# ==========================================================
# MAIN REPLY BUILDER
# ==========================================================

def generate_scn_reply(
    text: str,
    metadata: Dict[str, Any],
) -> Dict[str, Any]:

    text = text or ""

    metadata = metadata or {}

    # ------------------------------------------------------
    # ISSUE ANALYSIS
    # ------------------------------------------------------

    issue_analysis = build_issue_analysis(
        text=text,
        metadata=metadata,
    )

    issues = issue_analysis.get(
        "issues",
        [],
    )

    # ------------------------------------------------------
    # LEGAL MAPPING
    # ------------------------------------------------------

    legal_mapping = build_legal_mapping(
        text=text,
        issues=issues,
    )

    # ------------------------------------------------------
    # EVIDENCE MAPPING
    # ------------------------------------------------------

    evidence_mapping = map_evidence_to_issues(
        text=text,
        issues=issues,
    )

    taxpayer = _metadata_value(
        metadata,
        "taxpayer_name",
        "the Noticee",
    )

    notice_number = _metadata_value(
        metadata,
        "notice_number",
        "Not available",
    )

    gstin = _metadata_value(
        metadata,
        "gstin",
        "Not available",
    )

    # ------------------------------------------------------
    # HEADER
    # ------------------------------------------------------

    sections = []

    sections.append(
        "SUBJECT: REPLY TO SHOW CAUSE NOTICE"
    )

    sections.append(
        ""
        "Respected Sir/Madam,"
    )

    sections.append(
        ""
        f"On behalf of {taxpayer}, the present reply is "
        f"submitted in response to Show Cause Notice "
        f"bearing reference number {notice_number}. "
        f"The GSTIN identified from the source document is "
        f"{gstin}."
    )

    # ------------------------------------------------------
    # PRELIMINARY SUBMISSION
    # ------------------------------------------------------

    sections.append(
        ""
        "1. PRELIMINARY SUBMISSION\n\n"
        "The Noticee respectfully submits that the allegations "
        "contained in the Show Cause Notice are required to be "
        "considered on the basis of the complete facts, records, "
        "documents and applicable provisions of GST law. "
        "The Noticee reserves the right to supplement the "
        "present reply with additional documents and detailed "
        "submissions wherever necessary."
    )

    # ------------------------------------------------------
    # SOURCE DOCUMENT FACTS
    # ------------------------------------------------------

    sections.append(
        ""
        "2. FACTUAL PARTICULARS IDENTIFIED FROM THE NOTICE\n\n"
        + build_source_summary(metadata)
    )

    # ------------------------------------------------------
    # ISSUE-WISE REPLY
    # ------------------------------------------------------

    sections.append(
        ""
        "3. ISSUE-WISE RESPONSE TO THE ALLEGATIONS"
    )

    if issues:

        for issue in issues:

            sections.append(
                ""
                + build_issue_response(
                    issue
                )
            )

    else:

        sections.append(
            ""
            "No sufficiently structured allegation heading was "
            "extracted from the source document. The Noticee "
            "requests that each allegation in the SCN be examined "
            "separately with reference to the relied-upon "
            "documents and records."
        )

    # ------------------------------------------------------
    # LEGAL SUBMISSIONS
    # ------------------------------------------------------

    sections.append(
        ""
        "4. LEGAL SUBMISSIONS\n\n"
        + build_legal_submissions(
            legal_mapping
        )
    )

    # ------------------------------------------------------
    # SUPPORTING EVIDENCE
    # ------------------------------------------------------

    sections.append(
        ""
        "5. SUPPORTING DOCUMENTS AND EVIDENCE\n\n"
        + build_evidence_submissions(
            evidence_mapping
        )
    )

    # ------------------------------------------------------
    # DEMAND / STRUCTURED LITIGATION DATA
    # ------------------------------------------------------

    demand = issue_analysis.get(
        "demand",
        {},
    )

    sections.append(
        ""
        "6. DEMAND / LIABILITY\n\n"
        f"Tax: {_money(demand.get('tax'))}\n"
        f"Interest: {_money(demand.get('interest'))}\n"
        f"Penalty: {_money(demand.get('penalty'))}\n\n"
        "The above figures reflect only amounts explicitly "
        "extracted from demand-related source text. No amount "
        "has been invented where the source document did not "
        "provide a sufficiently identifiable figure.\n\n"
        + build_structured_demands(metadata)
    )

    # ------------------------------------------------------
    # TOTAL PROPOSED DEMAND
    # ------------------------------------------------------

    total_demand = metadata.get(
        "total_demand"
    )

    if total_demand is not None:

        try:
            total_demand_text = (
                f"₹{float(total_demand):,.2f}"
            )
        except (
            TypeError,
            ValueError,
        ):
            total_demand_text = (
                "Amount available in structured analysis"
            )

        sections.append(
            ""
            "6A. TOTAL PROPOSED DEMAND\n\n"
            f"Total proposed demand: "
            f"{total_demand_text}.\n\n"
            "This amount is reproduced from the "
            "structured demand extraction and has "
            "not been independently calculated."
        )

    # ------------------------------------------------------
    # STRUCTURED PENALTY PROPOSALS
    # ------------------------------------------------------

    sections.append(
        ""
        "7. STRUCTURED PENALTY PROPOSALS\n\n"
        + build_structured_penalties(metadata)
    )

    # ------------------------------------------------------
    # STRUCTURED ALLEGATIONS
    # ------------------------------------------------------

    sections.append(
        ""
        "8. STRUCTURED ALLEGATIONS\n\n"
        + build_structured_allegations(metadata)
    )

    # ------------------------------------------------------
    # PERSONAL HEARING
    # ------------------------------------------------------

    sections.append(
        ""
        "9. REQUEST FOR PERSONAL HEARING\n\n"
        "The Noticee respectfully requests an opportunity of "
        "personal hearing before adjudication so that the facts, "
        "documents, reconciliations and legal submissions may "
        "be fully explained."
    )

    # ------------------------------------------------------
    # PRAYER
    # ------------------------------------------------------

    sections.append(
        ""
        "10. PRAYER\n\n"
        + build_prayer()
    )

    # ------------------------------------------------------
    # CLOSING
    # ------------------------------------------------------

    sections.append(
        ""
        "Yours faithfully,\n\n"
        "Authorized Representative\n"
        f"For {taxpayer}"
    )

    reply = "\n\n".join(
        sections
    )

    # ------------------------------------------------------
    # VALIDATION
    # ------------------------------------------------------

    validation = validate_reply(
        reply=reply,
        metadata=metadata,
    )

    return {
        "reply": reply,
        "issue_analysis": issue_analysis,
        "legal_mapping": legal_mapping,
        "evidence_mapping": evidence_mapping,
        "validation": validation,
        "character_count": len(reply),
        "word_count": len(
            re.findall(
                r"\S+",
                reply,
            )
        ),
    }


# ==========================================================
# BACKWARD-COMPATIBLE FUNCTION
# ==========================================================

def generate_reply(
    text: str,
    metadata: Dict[str, Any],
) -> str:

    result = generate_scn_reply(
        text=text,
        metadata=metadata,
    )

    return result["reply"]
