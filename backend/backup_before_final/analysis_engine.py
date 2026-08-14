import re


def analyze_notice(
    text: str,
    metadata: dict,
):
    result = {}

    # --------------------------------------------------
    # Clean Text
    # --------------------------------------------------
    text = text or ""
    upper = text.upper()

    # --------------------------------------------------
    # Document Type
    # --------------------------------------------------
    if "SHOW CAUSE NOTICE" in upper or re.search(r"\bSCN\b", upper):
        document_type = "SCN"

    elif (
        "ORDER-IN-ORIGINAL" in upper
        or "ORDER IN ORIGINAL" in upper
        or re.search(r"\bOIO\b", upper)
    ):
        document_type = "OIO"

    elif "APPEAL" in upper:
        document_type = "Appeal"

    elif "DRC" in upper:
        document_type = "DRC"

    else:
        document_type = "Unknown"

    result["document_type"] = document_type

    # --------------------------------------------------
    # GST Sections
    # --------------------------------------------------
    section = metadata.get("section")

    section_text = str(section or "")

    section_numbers = re.findall(
        r"\b\d{1,3}[A-Za-z]?\b",
        section_text,
    )

    section_numbers = list(dict.fromkeys(section_numbers))

    result["sections"] = section_numbers

    # --------------------------------------------------
    # Risk Analysis
    # --------------------------------------------------
    risk = "Low"

    # Section 74 = High
    if "74" in section_numbers:
        risk = "High"

    # Section 73 = Medium
    elif "73" in section_numbers:
        risk = "Medium"

    # Section 16 = Medium
    elif "16" in section_numbers:
        risk = "Medium"

    # DRC / SCN generally requires attention
    elif document_type in ["SCN", "DRC"]:
        risk = "Medium"

    result["risk_level"] = risk

    # --------------------------------------------------
    # Reply Required
    # --------------------------------------------------
    result["reply_required"] = (
        document_type in ["SCN", "OIO", "DRC", "Appeal"]
    )

    # --------------------------------------------------
    # Metadata
    # --------------------------------------------------
    taxpayer = (
        metadata.get("taxpayer_name")
        or "Taxpayer"
    )

    financial_year = (
        metadata.get("financial_year")
        or "Not Available"
    )

    # --------------------------------------------------
    # Tax Amount
    # --------------------------------------------------
    tax_amount = metadata.get("tax_amount")

    # --------------------------------------------------
    # Summary
    # --------------------------------------------------
    sections_display = (
        ", ".join(section_numbers)
        if section_numbers
        else "Not Available"
    )

    result["summary"] = (
        f"{document_type} detected for {taxpayer}. "
        f"Applicable GST sections: {sections_display}. "
        f"Financial Year: {financial_year}. "
        f"Risk Level: {risk}."
    )

    # --------------------------------------------------
    # Recommendation
    # --------------------------------------------------
    if risk == "High":

        recommendation = (
            "Prepare a detailed reply with section-wise "
            "legal explanation, invoices, books of accounts, "
            "GSTR-1, GSTR-3B, GSTR-2A/2B reconciliation, "
            "payment records and other supporting evidence. "
            "The case should be reviewed carefully before "
            "submitting the reply."
        )

    elif risk == "Medium":

        recommendation = (
            "Review the GST notice carefully and reconcile "
            "the relevant GST records. Prepare supporting "
            "documents, invoices, returns and reconciliation "
            "statements before responding."
        )

    else:

        recommendation = (
            "Review the notice and maintain all relevant "
            "GST records and supporting documents."
        )

    result["recommendation"] = recommendation

    return result