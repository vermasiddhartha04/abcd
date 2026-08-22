import re
from typing import Any, Dict, List, Optional


# ==========================================================
# HELPERS
# ==========================================================

def clean_text(
    value: Optional[str],
) -> Optional[str]:

    if value is None:
        return None

    value = re.sub(
        r"\s+",
        " ",
        str(value),
    ).strip()

    return value if value else None


def unique(
    items: List[str],
) -> List[str]:

    result = []
    seen = set()

    for item in items:

        item = clean_text(item)

        if not item:
            continue

        key = item.lower()

        if key not in seen:

            seen.add(key)

            result.append(item)

    return result


# ==========================================================
# DOCUMENT CLASSIFICATION
# ==========================================================

def classify_document(
    text: str,
    metadata: Dict[str, Any],
) -> str:

    upper_text = (
        text or ""
    ).upper()

    metadata_type = str(
        metadata.get(
            "document_type"
        )
        or ""
    ).upper()

    # ------------------------------------------------------
    # DRC-01A
    # ------------------------------------------------------

    if (
        metadata_type == "DRC-01A"
        or "DRC-01A" in upper_text
        or "DRC 01A" in upper_text
        or "FORM GST DRC-01A" in upper_text
        or "FORM GST DRC 01A" in upper_text
    ):
        return "DRC-01A"

    # ------------------------------------------------------
    # SCN REPLY
    # ------------------------------------------------------

    if any(
        phrase in upper_text
        for phrase in [
            "REPLY TO SHOW CAUSE NOTICE",
            "REPLY TO THE SHOW CAUSE NOTICE",
            "RESPONSE TO SHOW CAUSE NOTICE",
            "SCN REPLY",
            "SUBMISSIONS IN RESPONSE TO SCN",
        ]
    ):
        return "SCN_REPLY"

    # ------------------------------------------------------
    # OIA
    # ------------------------------------------------------

    if (
        "ORDER-IN-APPEAL" in upper_text
        or "ORDER IN APPEAL" in upper_text
    ):
        return "OIA"

    # ------------------------------------------------------
    # OIO
    # ------------------------------------------------------

    if (
        "ORDER-IN-ORIGINAL" in upper_text
        or "ORDER IN ORIGINAL" in upper_text
    ):
        return "OIO"

    # ------------------------------------------------------
    # APPEAL
    # ------------------------------------------------------

    if any(
        phrase in upper_text
        for phrase in [
            "MEMORANDUM OF APPEAL",
            "APPEAL AGAINST ORDER",
            "GROUNDS OF APPEAL",
            "APPEAL PETITION",
            "APPEAL BEFORE THE",
        ]
    ):
        return "APPEAL"

    # ------------------------------------------------------
    # SCN
    # ------------------------------------------------------

    if (
        "SHOW CAUSE NOTICE" in upper_text
        or "SHOWCAUSE NOTICE" in upper_text
        or re.search(
            r"\bSCN\b",
            upper_text,
        )
    ):
        return "SCN"

    return "UNKNOWN"


# ==========================================================
# STAGE MAP
# ==========================================================

STAGE_MAP = {

    "DRC-01A": {

        "current_stage": "PRE_SCN",

        "next_stage": "SCN",

        "action_type": "PRE_SCN_RESPONSE",

        "action_label": (
            "Submit response or pay liability within 15 days"
        ),

        "reply_required": True,

        "appeal_required": False,
    },

    "SCN": {

        "current_stage": "SCN",

        "next_stage": "SCN_REPLY",

        "action_type": "SCN_REPLY",

        "action_label": "Prepare SCN Reply",

        "reply_required": True,

        "appeal_required": False,
    },

    "SCN_REPLY": {

        "current_stage": "SCN_REPLY",

        "next_stage": "OIO",

        "action_type": "OIO_REVIEW",

        "action_label": (
            "Review SCN Reply and prepare for adjudication"
        ),

        "reply_required": False,

        "appeal_required": False,
    },

    "OIO": {

        "current_stage": "OIO",

        "next_stage": "APPEAL",

        "action_type": "APPEAL_REVIEW",

        "action_label": (
            "Review OIO and evaluate appeal"
        ),

        "reply_required": False,

        "appeal_required": True,
    },

    "APPEAL": {

        "current_stage": "APPEAL",

        "next_stage": "OIA",

        "action_type": "OIA_TRACKING",

        "action_label": (
            "Track appeal and prepare for OIA"
        ),

        "reply_required": False,

        "appeal_required": False,
    },

    "OIA": {

        "current_stage": "OIA",

        "next_stage": "FINAL",

        "action_type": "FINAL_REVIEW",

        "action_label": (
            "Review Order-in-Appeal and determine final outcome"
        ),

        "reply_required": False,

        "appeal_required": False,
    },

    "UNKNOWN": {

        "current_stage": "UNKNOWN",

        "next_stage": None,

        "action_type": "MANUAL_REVIEW",

        "action_label": (
            "Review document manually and determine litigation stage"
        ),

        "reply_required": False,

        "appeal_required": False,
    },
}


# ==========================================================
# SECTION EXTRACTION
# ==========================================================

def extract_sections(
    text: str,
    metadata: Dict[str, Any],
) -> List[str]:

    sections = []

    metadata_section = metadata.get(
        "section"
    )

    if metadata_section:

        metadata_section = str(
            metadata_section
        ).strip()

        metadata_section = re.sub(
            r"^Section\s+Section\s+",
            "Section ",
            metadata_section,
            flags=re.IGNORECASE,
        )

        sections.append(
            metadata_section
        )

    patterns = [
        r"\bSection\s+(\d+[A-Z]?(?:\([0-9A-Z]+\))?)",
        r"\bSec\.?\s+(\d+[A-Z]?(?:\([0-9A-Z]+\))?)",
    ]

    for pattern in patterns:

        matches = re.findall(
            pattern,
            text or "",
            re.IGNORECASE,
        )

        for match in matches:

            sections.append(
                f"Section {match}"
            )

    return unique(
        sections
    )


# ==========================================================
# ISSUE
# ==========================================================

def detect_issue(
    text: str,
) -> str:

    upper_text = (
        text or ""
    ).upper()

    if (
        "180 DAYS" in upper_text
        and (
            "ITC" in upper_text
            or "INPUT TAX CREDIT" in upper_text
        )
    ):
        return (
            "Ineligible ITC due to non-payment "
            "to vendors within 180 days"
        )

    if (
        "INELIGIBLE ITC" in upper_text
        or "INELIGIBLE INPUT TAX CREDIT" in upper_text
    ):
        return "Ineligible Input Tax Credit"

    if (
        "INPUT TAX CREDIT" in upper_text
        or re.search(
            r"\bITC\b",
            upper_text,
        )
    ):
        return "Input Tax Credit related issue"

    if (
        "TAX EVASION" in upper_text
        or "EVASION OF TAX" in upper_text
    ):
        return "Tax evasion"

    if (
        "SHORT PAYMENT" in upper_text
        or "SHORT PAID" in upper_text
    ):
        return "Short payment of tax"

    if "WRONGFUL AVAILMENT" in upper_text:
        return "Wrongful availment of ITC"

    if "REFUND" in upper_text:
        return "GST refund related issue"

    return "GST compliance issue"


# ==========================================================
# ISSUE CATEGORY
# ==========================================================

def detect_issue_category(
    text: str,
) -> str:

    upper_text = (
        text or ""
    ).upper()

    if (
        "ITC" in upper_text
        or "INPUT TAX CREDIT" in upper_text
    ):
        return "ITC"

    if "REFUND" in upper_text:
        return "REFUND"

    if (
        "TAX EVASION" in upper_text
        or "EVASION OF TAX" in upper_text
    ):
        return "TAX EVASION"

    if "REGISTRATION" in upper_text:
        return "REGISTRATION"

    if "CLASSIFICATION" in upper_text:
        return "CLASSIFICATION"

    return "GST COMPLIANCE"


# ==========================================================
# RISK CALCULATION
# ==========================================================

def calculate_risk(
    document_type: str,
    text: str,
    metadata: Dict[str, Any],
) -> str:

    upper_text = (
        text or ""
    ).upper()

    score = 0

    # ------------------------------------------------------
    # DRC-01A / SCN litigation stage
    # ------------------------------------------------------

    if document_type == "DRC-01A":
        score += 3

    elif document_type == "SCN":
        score += 4

    elif document_type in {
        "OIO",
        "APPEAL",
        "OIA",
    }:
        score += 4

    # ------------------------------------------------------
    # Section 74
    # ------------------------------------------------------

    if re.search(
        r"\bSECTION\s+74\b",
        upper_text,
    ):
        score += 3

    # ------------------------------------------------------
    # Fraud / suppression
    # ------------------------------------------------------

    high_risk_terms = [
        "FRAUD",
        "SUPPRESSION",
        "WILFUL MISSTATEMENT",
        "WILLFUL MISSTATEMENT",
        "INTENT TO EVADE",
        "EVASION OF TAX",
    ]

    for term in high_risk_terms:

        if term in upper_text:

            score += 3

            break

    # ------------------------------------------------------
    # ITC issue
    # ------------------------------------------------------

    if (
        "INPUT TAX CREDIT" in upper_text
        or re.search(
            r"\bITC\b",
            upper_text,
        )
    ):
        score += 2

    # ------------------------------------------------------
    # 180 DAYS
    # ------------------------------------------------------

    if "180 DAYS" in upper_text:
        score += 2

    # ------------------------------------------------------
    # Financial exposure
    # ------------------------------------------------------

    amount = metadata.get(
        "tax_amount"
    )

    try:

        if amount is not None:

            numeric_amount = float(
                amount
            )

            if numeric_amount >= 10_000_000:
                score += 4

            elif numeric_amount >= 1_000_000:
                score += 3

            elif numeric_amount > 0:
                score += 1

    except (
        TypeError,
        ValueError,
    ):
        pass

    # ------------------------------------------------------
    # Penalty
    # ------------------------------------------------------

    penalty = metadata.get(
        "penalty"
    )

    try:

        if (
            penalty is not None
            and float(penalty) > 0
        ):
            score += 1

    except (
        TypeError,
        ValueError,
    ):
        pass

    # ------------------------------------------------------
    # Final
    # ------------------------------------------------------

    if score >= 7:
        return "High"

    if score >= 4:
        return "Medium"

    return "Low"


# ==========================================================
# SUMMARY
# ==========================================================

def build_summary(
    document_type: str,
    current_stage: str,
    next_stage: Optional[str],
    metadata: Dict[str, Any],
    issue: str,
    sections: List[str],
    risk_level: str,
) -> str:

    taxpayer = (
        metadata.get(
            "taxpayer_name"
        )
        or "Taxpayer not identified"
    )

    gstin = (
        metadata.get(
            "gstin"
        )
        or "GSTIN not identified"
    )

    notice_number = (
        metadata.get(
            "notice_number"
        )
        or "Notice number not identified"
    )

    # ------------------------------------------------------
    # DEMAND-AWARE AMOUNT
    #
    # Prefer explicit metadata tax_amount.
    # If unavailable, use the validated structured
    # total_demand extracted from demand_extractor.py.
    # ------------------------------------------------------

    tax_amount = metadata.get(
        "tax_amount"
    )

    total_demand = metadata.get(
        "total_demand"
    )

    effective_amount = (
        tax_amount
        if tax_amount is not None
        else total_demand
    )

    if effective_amount is not None:

        try:

            formatted_amount = (
                f"{float(effective_amount):,.2f}"
            )

            if tax_amount is not None:

                amount_text = (
                    f"Proposed tax amount: "
                    f"₹{formatted_amount}."
                )

            else:

                amount_text = (
                    f"Total proposed demand: "
                    f"₹{formatted_amount}."
                )

        except (
            TypeError,
            ValueError,
        ):

            amount_text = (
                "Proposed demand amount is available."
            )

    else:

        amount_text = (
            "Proposed demand amount is not available."
        )

    section_text = (
        ", ".join(sections)
        if sections
        else "No specific GST section extracted."
    )

    next_stage_text = (
        next_stage
        if next_stage
        else "Manual review required"
    )

    return (
        f"{document_type} document detected for "
        f"{taxpayer}. "
        f"GSTIN: {gstin}. "
        f"Notice Number: {notice_number}. "
        f"Current litigation stage: "
        f"{current_stage}. "
        f"Next stage: "
        f"{next_stage_text}. "
        f"Main issue: "
        f"{issue}. "
        f"Applicable GST sections: "
        f"{section_text}. "
        f"{amount_text} "
        f"Risk Level: "
        f"{risk_level}."
    )


# ==========================================================
# RECOMMENDATION
# ==========================================================

def build_recommendation(
    document_type: str,
    issue: str,
    risk_level: str,
) -> str:

    if document_type == "DRC-01A":

        return (
            "Review the pre-SCN intimation carefully, "
            "verify the proposed liability with GST records, "
            "and submit the required response or payment "
            "within the specified time."
        )

    if document_type == "SCN":

        return (
            "Review the SCN carefully and prepare factual "
            "and legally supported submissions with relevant "
            "GST records and supporting evidence to rebut "
            "the allegations and seek withdrawal of the "
            "proposed demand."
        )

    if document_type == "SCN_REPLY":

        return (
            "Review the SCN Reply and supporting evidence "
            "and prepare for adjudication and the "
            "Order-in-Original."
        )

    if document_type == "OIO":

        return (
            "Review the Order-in-Original and determine "
            "whether an appeal should be filed based on "
            "the findings on facts and law."
        )

    if document_type == "APPEAL":

        return (
            "Review the grounds of appeal, supporting "
            "documents and appellate proceedings and "
            "prepare for the Order-in-Appeal."
        )

    if document_type == "OIA":

        return (
            "Review the Order-in-Appeal and determine "
            "whether any further legal action is required."
        )

    return (
        "Review the document manually and determine "
        "the appropriate GST litigation stage and action."
    )


# ==========================================================
# MAIN ANALYSIS
# ==========================================================

def analyze_notice(
    text: str,
    metadata: Dict[str, Any],
) -> Dict[str, Any]:

    text = text or ""

    # ------------------------------------------------------
    # DOCUMENT
    # ------------------------------------------------------

    document_type = classify_document(
        text=text,
        metadata=metadata,
    )

    # ------------------------------------------------------
    # STAGE
    # ------------------------------------------------------

    stage = STAGE_MAP.get(
        document_type,
        STAGE_MAP["UNKNOWN"],
    )

    current_stage = stage[
        "current_stage"
    ]

    next_stage = stage[
        "next_stage"
    ]

    action_type = stage[
        "action_type"
    ]

    action_label = stage[
        "action_label"
    ]

    # ------------------------------------------------------
    # SECTIONS
    # ------------------------------------------------------

    sections = extract_sections(
        text=text,
        metadata=metadata,
    )

    # ------------------------------------------------------
    # ISSUE
    # ------------------------------------------------------

    issue = detect_issue(
        text
    )

    issue_category = detect_issue_category(
        text
    )

    # ------------------------------------------------------
    # RISK
    # ------------------------------------------------------

    risk_level = calculate_risk(
        document_type=document_type,
        text=text,
        metadata=metadata,
    )

    # ------------------------------------------------------
    # SUMMARY
    # ------------------------------------------------------

    summary = build_summary(
        document_type=document_type,
        current_stage=current_stage,
        next_stage=next_stage,
        metadata=metadata,
        issue=issue,
        sections=sections,
        risk_level=risk_level,
    )

    # ------------------------------------------------------
    # RECOMMENDATION
    # ------------------------------------------------------

    recommendation = build_recommendation(
        document_type=document_type,
        issue=issue,
        risk_level=risk_level,
    )

    # ------------------------------------------------------
    # FINAL
    # ------------------------------------------------------

    return {

        "document_type": document_type,

        "current_stage": current_stage,

        "next_stage": next_stage,

        "action_type": action_type,

        "action_label": action_label,

        "reply_required": stage[
            "reply_required"
        ],

        "appeal_required": stage[
            "appeal_required"
        ],

        "risk_level": risk_level,

        "summary": summary,

        "recommendation": recommendation,

        "sections": sections,

        "issue_category": issue_category,

        "issue": issue,
    }
