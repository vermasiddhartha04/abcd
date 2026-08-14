import re


def clean_text(text: str) -> str:
    """
    Normalize extracted PDF/OCR text.
    """

    if not text:
        return ""

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Common PDF/OCR currency replacement
    text = text.replace("■", "₹")

    # Normalize spaces/tabs but preserve line breaks
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def search(pattern: str, text: str):
    """
    Return first regex capture group.
    """

    match = re.search(
        pattern,
        text,
        re.IGNORECASE | re.MULTILINE,
    )

    if match:
        return match.group(1).strip()

    return None


def extract_amount(pattern: str, text: str):
    """
    Extract monetary amount.

    Supports:
    ₹12,45,780
    INR 12,45,780
    Rs 12,45,780
    12,45,780
    """

    value = search(pattern, text)

    if not value:
        return None

    value = value.replace("₹", "")
    value = value.replace("INR", "")
    value = value.replace("Rs.", "")
    value = value.replace("Rs", "")
    value = value.replace(",", "")
    value = value.replace(" ", "")

    try:
        float(value)
        return value
    except ValueError:
        return None


def extract_labeled_value(labels, text: str):
    """
    Extract text appearing after a label.

    Supports:

    Taxpayer: ABC Manufacturing Pvt Ltd

    and:

    Taxpayer
    ABC Manufacturing Pvt Ltd
    """

    for label in labels:

        # ------------------------------------------
        # Same-line format
        # ------------------------------------------

        pattern_same_line = (
            rf"{label}"
            r"\s*[:\-]\s*"
            r"([^\n]+)"
        )

        value = search(
            pattern_same_line,
            text,
        )

        if value:
            value = value.strip()

            if value:
                return value

        # ------------------------------------------
        # Next-line format
        # ------------------------------------------

        pattern_next_line = (
            rf"{label}"
            r"\s*\n\s*"
            r"([^\n]+)"
        )

        value = search(
            pattern_next_line,
            text,
        )

        if value:
            value = value.strip()

            if value:
                return value

    return None


def extract_amount_by_labels(labels, text: str):
    """
    Extract amount from GST notice.

    Supports:

    Tax Proposed: INR 12,45,780

    and:

    Tax Proposed
    INR 12,45,780
    """

    for label in labels:

        # ------------------------------------------
        # Same-line amount
        # ------------------------------------------

        pattern_same_line = (
            rf"{label}"
            r"\s*[:\-]?\s*"
            r"(?:₹|INR|Rs\.?)?"
            r"\s*"
            r"([\d,]+(?:\.\d+)?)"
        )

        value = extract_amount(
            pattern_same_line,
            text,
        )

        if value:
            return value

        # ------------------------------------------
        # Next-line amount
        # ------------------------------------------

        pattern_next_line = (
            rf"{label}"
            r"\s*\n\s*"
            r"(?:₹|INR|Rs\.?)?"
            r"\s*"
            r"([\d,]+(?:\.\d+)?)"
        )

        value = extract_amount(
            pattern_next_line,
            text,
        )

        if value:
            return value

    return None


def extract_gst_metadata(text: str):
    """
    Extract GST litigation metadata from
    PDF/OCR extracted text.
    """

    text = clean_text(text)

    metadata = {}

    # ==================================================
    # GSTIN
    # ==================================================

    gstin = re.search(
        r"\b\d{2}[A-Z]{5}\d{4}[A-Z][A-Z0-9]Z[A-Z0-9]\b",
        text,
        re.IGNORECASE,
    )

    metadata["gstin"] = (
        gstin.group().upper()
        if gstin
        else None
    )

    # ==================================================
    # PAN
    # ==================================================

    pan = re.search(
        r"\b[A-Z]{5}\d{4}[A-Z]\b",
        text,
        re.IGNORECASE,
    )

    metadata["pan"] = (
        pan.group().upper()
        if pan
        else None
    )

    # ==================================================
    # Taxpayer Name
    # ==================================================

    metadata["taxpayer_name"] = extract_labeled_value(
        [
            r"Taxpayer",
            r"Taxpayer\s*Name",
            r"Legal\s*Name\s*of\s*Business",
            r"Legal\s*Name",
            r"Trade\s*Name",
            r"Name\s*of\s*Taxpayer",
            r"Taxable\s*Person",
        ],
        text,
    )

    # ------------------------------------------
    # Validate taxpayer value
    # ------------------------------------------

    if metadata["taxpayer_name"]:

        value = metadata["taxpayer_name"].strip()

        invalid_values = {
            "pan",
            "gstin",
            "notice",
            "notice type",
            "financial year",
            "status",
            "taxpayer",
            "taxpayer name",
            "name",
            "notice number",
            "notice date",
            "document type",
        }

        if value.lower() in invalid_values:

            metadata["taxpayer_name"] = None

        else:

            # Remove accidental trailing fields
            value = re.split(
                r"\b(?:PAN|GSTIN|Notice Number|Notice Date|"
                r"Document Type|Financial Year|Tax Period|"
                r"Sections|Tax Proposed|Interest Proposed|"
                r"Penalty Proposed|Total Demand|Jurisdiction|"
                r"Status)\b",
                value,
                maxsplit=1,
                flags=re.IGNORECASE,
            )[0].strip()

            metadata["taxpayer_name"] = (
                value if value else None
            )

    # ==================================================
    # Financial Year
    # ==================================================

    metadata["financial_year"] = search(
        r"(?:Financial\s*Year|FY)"
        r"\s*[:\-]?\s*"
        r"(20\d{2}\s*-\s*\d{2})",
        text,
    )

    if metadata["financial_year"]:

        metadata["financial_year"] = re.sub(
            r"\s+",
            "",
            metadata["financial_year"],
        )

    # ==================================================
    # Tax Period
    # ==================================================

    metadata["tax_period"] = extract_labeled_value(
        [
            r"Tax\s*Period",
            r"Taxable\s*Period",
        ],
        text,
    )

    # ==================================================
    # Notice Number
    # ==================================================

    metadata["notice_number"] = None

    notice_patterns = [

        r"Notice\s*Reference"
        r"\s*[:\-]?\s*"
        r"([A-Za-z0-9\/\-_]+)",

        r"Notice\s*(?:No|Number)"
        r"\s*[:\-]?\s*"
        r"([A-Za-z0-9\/\-_]+)",

        r"SCN\s*(?:No|Number)"
        r"\s*[:\-]?\s*"
        r"([A-Za-z0-9\/\-_]+)",

        r"Reference\s*(?:No|Number)"
        r"\s*[:\-]?\s*"
        r"([A-Za-z0-9\/\-_]+)",

        r"\b(SCN\/[A-Za-z0-9\/\-_]+)",
    ]

    for pattern in notice_patterns:

        value = search(
            pattern,
            text,
        )

        if value:

            metadata["notice_number"] = value.strip()

            break

    # ==================================================
    # Document Type
    # ==================================================

    upper_text = text.upper()

    if (
        "SHOW CAUSE NOTICE" in upper_text
        or re.search(
            r"\bSCN\b",
            upper_text,
        )
    ):

        metadata["document_type"] = "SCN"

    elif (
        "ORDER-IN-ORIGINAL" in upper_text
        or "ORDER IN ORIGINAL" in upper_text
        or re.search(
            r"\bOIO\b",
            upper_text,
        )
    ):

        metadata["document_type"] = "OIO"

    elif re.search(
        r"\bAPPEAL\b",
        upper_text,
    ):

        metadata["document_type"] = "Appeal"

    elif re.search(
        r"\bDRC\b",
        upper_text,
    ):

        metadata["document_type"] = "DRC"

    else:

        metadata["document_type"] = None

    # ==================================================
    # GST Sections
    # ==================================================

    metadata["section"] = None

    section_patterns = [

        r"Applicable\s*GST\s*Sections?"
        r"\s*[:\-]?\s*"
        r"([0-9]+(?:\s*,\s*[0-9]+)*)",

        r"GST\s*Sections?"
        r"\s*[:\-]?\s*"
        r"([0-9]+(?:\s*,\s*[0-9]+)*)",

        r"Sections?"
        r"\s*[:\-]?\s*"
        r"([0-9]+(?:\s*,\s*[0-9]+)*)",

        r"Section"
        r"\s+"
        r"([0-9]+(?:\s*,\s*[0-9]+)*)",
    ]

    for pattern in section_patterns:

        value = search(
            pattern,
            text,
        )

        if value:

            # Normalize comma spacing:
            # 73, 74,16, 17, 50
            # becomes:
            # 73, 74, 16, 17, 50

            metadata["section"] = re.sub(
                r"\s*,\s*",
                ", ",
                value.strip(),
            )

            break

    # ==================================================
    # Tax Amount
    # ==================================================

    metadata["tax_amount"] = extract_amount_by_labels(
        [
            r"Tax\s*Proposed",
            r"Tax\s*Amount",
            r"Tax\s*Demand",
            r"Tax\s*Liability",
            r"Total\s*Tax",
        ],
        text,
    )

    # ==================================================
    # Interest
    # ==================================================

    metadata["interest"] = extract_amount_by_labels(
        [
            r"Interest\s*Proposed",
            r"Interest\s*Amount",
            r"Interest\s*Demand",
            r"Interest",
        ],
        text,
    )

    # ==================================================
    # Penalty
    # ==================================================

    metadata["penalty"] = extract_amount_by_labels(
        [
            r"Penalty\s*Proposed",
            r"Penalty\s*Amount",
            r"Penalty\s*Demand",
            r"Penalty",
        ],
        text,
    )

    return metadata