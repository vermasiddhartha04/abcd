import re


# ============================================================
# DOCUMENT TYPE DETECTION
# ============================================================

def detect_document_type(text: str) -> str:
    """
    Detect GST litigation document type.

    Supported:
    - SCN
    - OIO
    - APPEAL
    - OIA
    - DRC
    - UNKNOWN

    Detection priority:

        OIA
          ↓
        APPEAL
          ↓
        OIO
          ↓
        SCN
          ↓
        DRC

    Important:
    An Appeal document can contain the words
    "Order-in-Original" because the Appeal may challenge
    the OIO.

    Therefore APPEAL must be checked before OIO.
    """

    text = text or ""
    upper = text.upper()

    # --------------------------------------------------------
    # OIA
    #
    # OIA must be checked first because an OIA document
    # can also contain the word "Appeal".
    # --------------------------------------------------------

    if (
        "ORDER-IN-APPEAL" in upper
        or "ORDER IN APPEAL" in upper
        or re.search(r"\bOIA\b", upper)
    ):
        return "OIA"

    # --------------------------------------------------------
    # APPEAL
    #
    # IMPORTANT:
    # Check Appeal BEFORE OIO.
    #
    # Example:
    #
    # "MEMORANDUM OF APPEAL
    #  against Order-in-Original"
    #
    # This must be detected as APPEAL, not OIO.
    # --------------------------------------------------------

    if (
        "MEMORANDUM OF APPEAL" in upper
        or "GROUNDS OF APPEAL" in upper
        or "NOTICE OF APPEAL" in upper
        or "APPEAL AGAINST" in upper
        or re.search(r"\bAPPEAL\b", upper)
    ):
        return "APPEAL"

    # --------------------------------------------------------
    # OIO
    # --------------------------------------------------------

    if (
        "ORDER-IN-ORIGINAL" in upper
        or "ORDER IN ORIGINAL" in upper
        or re.search(r"\bOIO\b", upper)
    ):
        return "OIO"

    # --------------------------------------------------------
    # SCN
    # --------------------------------------------------------

    if (
        "SHOW CAUSE NOTICE" in upper
        or re.search(r"\bSCN\b", upper)
    ):
        return "SCN"

    # --------------------------------------------------------
    # DRC
    # --------------------------------------------------------

    if re.search(r"\bDRC[- ]?\d", upper):
        return "DRC"

    # --------------------------------------------------------
    # UNKNOWN
    # --------------------------------------------------------

    return "UNKNOWN"


# ============================================================
# SECTION EXTRACTION
# ============================================================

def extract_sections(metadata: dict) -> list:
    """
    Extract unique GST section numbers from metadata.
    """

    section = metadata.get("section")

    if not section:
        return []

    section_text = str(section)

    sections = re.findall(
        r"\b\d{1,3}[A-Za-z]?\b",
        section_text,
    )

    # Remove duplicates while preserving order
    return list(dict.fromkeys(sections))


# ============================================================
# RISK ANALYSIS
# ============================================================

def calculate_risk(
    document_type: str,
    sections: list,
    metadata: dict,
) -> str:
    """
    Calculate basic litigation risk.

    Rules:

    Section 74
        → High

    Section 73 / 16
        → Medium

    Litigation documents
        → Medium

    Unknown
        → Low
    """

    section_set = set(sections)

    # --------------------------------------------------------
    # Highest priority
    # --------------------------------------------------------

    if "74" in section_set:
        return "High"

    # --------------------------------------------------------
    # Section 73 / 16
    # --------------------------------------------------------

    if (
        "73" in section_set
        or "16" in section_set
    ):
        return "Medium"

    # --------------------------------------------------------
    # Litigation-stage documents
    # --------------------------------------------------------

    if document_type in {
        "SCN",
        "OIO",
        "APPEAL",
        "OIA",
        "DRC",
    }:
        return "Medium"

    return "Low"


# ============================================================
# ACTION / NEXT STAGE
# ============================================================

def get_next_action(document_type: str) -> dict:
    """
    Decide the next GST litigation action.
    """

    actions = {

        # ----------------------------------------------------
        # SCN
        # ----------------------------------------------------

        "SCN": {
            "action_type": "SCN_REPLY",
            "action_label": "Prepare SCN Reply",
            "next_stage": "SCN_REPLY",
            "reply_required": True,
            "appeal_required": False,
        },

        # ----------------------------------------------------
        # OIO
        # ----------------------------------------------------

        "OIO": {
            "action_type": "APPEAL",
            "action_label": "Review OIO and Prepare Appeal",
            "next_stage": "APPEAL",
            "reply_required": False,
            "appeal_required": True,
        },

        # ----------------------------------------------------
        # APPEAL
        # ----------------------------------------------------

        "APPEAL": {
            "action_type": "OIA_REVIEW",
            "action_label": "Review Appeal and Await OIA",
            "next_stage": "OIA",
            "reply_required": False,
            "appeal_required": False,
        },

        # ----------------------------------------------------
        # OIA
        # ----------------------------------------------------

        "OIA": {
            "action_type": "FINAL_REVIEW",
            "action_label": "Review OIA and Determine Further Remedy",
            "next_stage": "FINAL",
            "reply_required": False,
            "appeal_required": False,
        },

        # ----------------------------------------------------
        # DRC
        # ----------------------------------------------------

        "DRC": {
            "action_type": "DRC_REVIEW",
            "action_label": "Review DRC Document",
            "next_stage": "DRC_REVIEW",
            "reply_required": False,
            "appeal_required": False,
        },

        # ----------------------------------------------------
        # UNKNOWN
        # ----------------------------------------------------

        "UNKNOWN": {
            "action_type": "MANUAL_REVIEW",
            "action_label": "Manual Document Review Required",
            "next_stage": "UNKNOWN",
            "reply_required": False,
            "appeal_required": False,
        },
    }

    return actions.get(
        document_type,
        actions["UNKNOWN"],
    )


# ============================================================
# SCN ANALYSIS
# ============================================================

def analyze_scn(
    metadata: dict,
    sections: list,
    risk: str,
) -> dict:
    """
    Analyze Show Cause Notice.
    """

    taxpayer = (
        metadata.get("taxpayer_name")
        or "Taxpayer"
    )

    financial_year = (
        metadata.get("financial_year")
        or "Not Available"
    )

    notice_number = (
        metadata.get("notice_number")
        or "Not Available"
    )

    sections_display = (
        ", ".join(sections)
        if sections
        else "Not Available"
    )

    summary = (
        f"SCN detected for {taxpayer}. "
        f"Notice Number: {notice_number}. "
        f"Applicable GST sections: {sections_display}. "
        f"Financial Year: {financial_year}. "
        f"Risk Level: {risk}."
    )

    if risk == "High":

        recommendation = (
            "Prepare a detailed SCN reply with factual "
            "explanations, section-wise legal arguments, "
            "invoices, books of accounts, GST returns, "
            "GSTR-1, GSTR-3B, GSTR-2A/2B reconciliation, "
            "payment records and other supporting evidence. "
            "The proposed tax, interest and penalty should "
            "be reviewed against the available records."
        )

    else:

        recommendation = (
            "Review the SCN carefully and prepare factual "
            "and legally supported submissions with relevant "
            "GST records and supporting evidence."
        )

    return {
        "summary": summary,
        "recommendation": recommendation,
        "reply_required": True,
        "appeal_required": False,
    }


# ============================================================
# OIO ANALYSIS
# ============================================================

def analyze_oio(
    metadata: dict,
    sections: list,
    risk: str,
) -> dict:
    """
    Analyze Order-in-Original.
    """

    taxpayer = (
        metadata.get("taxpayer_name")
        or "Taxpayer"
    )

    financial_year = (
        metadata.get("financial_year")
        or "Not Available"
    )

    notice_number = (
        metadata.get("notice_number")
        or "Not Available"
    )

    sections_display = (
        ", ".join(sections)
        if sections
        else "Not Available"
    )

    summary = (
        f"OIO detected for {taxpayer}. "
        f"Reference Number: {notice_number}. "
        f"Applicable GST sections: {sections_display}. "
        f"Financial Year: {financial_year}. "
        f"Risk Level: {risk}."
    )

    recommendation = (
        "Review the Order-in-Original against the SCN, "
        "taxpayer's reply and supporting evidence. "
        "Identify the findings of the adjudicating authority, "
        "the demand confirmed, modified or dropped, and "
        "evaluate potential grounds for appeal."
    )

    return {
        "summary": summary,
        "recommendation": recommendation,
        "reply_required": False,
        "appeal_required": True,
    }


# ============================================================
# APPEAL ANALYSIS
# ============================================================

def analyze_appeal(
    metadata: dict,
    sections: list,
    risk: str,
) -> dict:
    """
    Analyze Appeal document.
    """

    taxpayer = (
        metadata.get("taxpayer_name")
        or "Taxpayer"
    )

    financial_year = (
        metadata.get("financial_year")
        or "Not Available"
    )

    notice_number = (
        metadata.get("notice_number")
        or "Not Available"
    )

    sections_display = (
        ", ".join(sections)
        if sections
        else "Not Available"
    )

    summary = (
        f"Appeal document detected for {taxpayer}. "
        f"Reference Number: {notice_number}. "
        f"Applicable GST sections: {sections_display}. "
        f"Financial Year: {financial_year}. "
        f"Risk Level: {risk}."
    )

    recommendation = (
        "Review the challenged Order-in-Original, "
        "identify disputed findings and formulate "
        "fact-based and legally supported grounds of "
        "appeal. Supporting documents and the relief "
        "sought should be reviewed before filing."
    )

    return {
        "summary": summary,
        "recommendation": recommendation,
        "reply_required": False,
        "appeal_required": False,
    }


# ============================================================
# OIA ANALYSIS
# ============================================================

def analyze_oia(
    metadata: dict,
    sections: list,
    risk: str,
) -> dict:
    """
    Analyze Order-in-Appeal.
    """

    taxpayer = (
        metadata.get("taxpayer_name")
        or "Taxpayer"
    )

    financial_year = (
        metadata.get("financial_year")
        or "Not Available"
    )

    notice_number = (
        metadata.get("notice_number")
        or "Not Available"
    )

    sections_display = (
        ", ".join(sections)
        if sections
        else "Not Available"
    )

    summary = (
        f"OIA detected for {taxpayer}. "
        f"Reference Number: {notice_number}. "
        f"Applicable GST sections: {sections_display}. "
        f"Financial Year: {financial_year}. "
        f"Risk Level: {risk}."
    )

    recommendation = (
        "Review the Order-in-Appeal against the "
        "Order-in-Original and grounds of appeal. "
        "Determine whether the original order was upheld, "
        "modified or set aside and identify the appropriate "
        "next legal action."
    )

    return {
        "summary": summary,
        "recommendation": recommendation,
        "reply_required": False,
        "appeal_required": False,
    }


# ============================================================
# DRC ANALYSIS
# ============================================================

def analyze_drc(
    metadata: dict,
    sections: list,
    risk: str,
) -> dict:
    """
    Analyze DRC document.
    """

    taxpayer = (
        metadata.get("taxpayer_name")
        or "Taxpayer"
    )

    financial_year = (
        metadata.get("financial_year")
        or "Not Available"
    )

    summary = (
        f"DRC document detected for {taxpayer}. "
        f"Financial Year: {financial_year}. "
        f"Risk Level: {risk}."
    )

    recommendation = (
        "Review the DRC document, payment status, "
        "demand details and applicable GST records. "
        "Determine the appropriate compliance or "
        "litigation action."
    )

    return {
        "summary": summary,
        "recommendation": recommendation,
        "reply_required": False,
        "appeal_required": False,
    }


# ============================================================
# MAIN ANALYSIS FUNCTION
# ============================================================

def analyze_notice(
    text: str,
    metadata: dict,
):
    """
    Main GST litigation analysis function.

    Supports:

    SCN
    OIO
    APPEAL
    OIA
    DRC
    UNKNOWN
    """

    text = text or ""
    metadata = metadata or {}

    # --------------------------------------------------------
    # 1. Detect document type
    # --------------------------------------------------------

    document_type = detect_document_type(
        text
    )

    # --------------------------------------------------------
    # 2. Extract GST sections
    # --------------------------------------------------------

    sections = extract_sections(
        metadata
    )

    # --------------------------------------------------------
    # 3. Calculate risk
    # --------------------------------------------------------

    risk = calculate_risk(
        document_type=document_type,
        sections=sections,
        metadata=metadata,
    )

    # --------------------------------------------------------
    # 4. Document-specific analysis
    # --------------------------------------------------------

    if document_type == "SCN":

        analysis = analyze_scn(
            metadata=metadata,
            sections=sections,
            risk=risk,
        )

    elif document_type == "OIO":

        analysis = analyze_oio(
            metadata=metadata,
            sections=sections,
            risk=risk,
        )

    elif document_type == "APPEAL":

        analysis = analyze_appeal(
            metadata=metadata,
            sections=sections,
            risk=risk,
        )

    elif document_type == "OIA":

        analysis = analyze_oia(
            metadata=metadata,
            sections=sections,
            risk=risk,
        )

    elif document_type == "DRC":

        analysis = analyze_drc(
            metadata=metadata,
            sections=sections,
            risk=risk,
        )

    else:

        analysis = {
            "summary": (
                "The uploaded document could not be "
                "reliably classified as SCN, OIO, Appeal "
                "or OIA."
            ),
            "recommendation": (
                "Manual document review is required. "
                "Verify the document type and relevant "
                "GST litigation stage."
            ),
            "reply_required": False,
            "appeal_required": False,
        }

    # --------------------------------------------------------
    # 5. Determine next action
    # --------------------------------------------------------

    action = get_next_action(
        document_type
    )

    # --------------------------------------------------------
    # 6. Final analysis result
    # --------------------------------------------------------

    return {
        "document_type": document_type,

        "sections": sections,

        "risk_level": risk,

        "summary": analysis.get(
            "summary"
        ),

        "recommendation": analysis.get(
            "recommendation"
        ),

        "reply_required": analysis.get(
            "reply_required",
            action.get(
                "reply_required",
                False,
            ),
        ),

        "appeal_required": analysis.get(
            "appeal_required",
            action.get(
                "appeal_required",
                False,
            ),
        ),

        "action_type": action.get(
            "action_type"
        ),

        "action_label": action.get(
            "action_label"
        ),

        "next_stage": action.get(
            "next_stage"
        ),
    }