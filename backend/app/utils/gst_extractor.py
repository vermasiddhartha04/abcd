import re
from typing import Optional


# ==========================================================
# BASIC HELPERS
# ==========================================================

def _clean_text(value):
    if value is None:
        return None

    value = str(value)

    value = value.replace("\x00", " ")

    value = re.sub(
        r"[ \t]+",
        " ",
        value,
    )

    value = re.sub(
        r"\n{3,}",
        "\n\n",
        value,
    )

    return value.strip()


def _clean_line(value):
    if value is None:
        return None

    value = re.sub(
        r"\s+",
        " ",
        str(value),
    )

    return value.strip(
        " :-|,;"
    )


def _clean_number(value):
    if not value:
        return None

    value = str(value)

    value = (
        value
        .replace(",", "")
        .replace("₹", "")
        .replace("Rs.", "")
        .replace("Rs", "")
        .replace("/-", "")
        .strip()
    )

    try:
        return float(value)
    except (
        ValueError,
        TypeError,
    ):
        return None


def _unique(values):
    result = []

    for value in values:

        if value is None:
            continue

        if value not in result:
            result.append(value)

    return result


def _normalise_ocr(text):
    text = text or ""

    # Common OCR variants
    replacements = {
        "GSTlN": "GSTIN",
        "GSTlN.": "GSTIN",
        "G5TIN": "GSTIN",
        "G5T1N": "GSTIN",
        "GST IN": "GSTIN",
        "S.C.N.": "SCN",
        "S.C.N": "SCN",
        "Show Cause Notice": "SHOW CAUSE NOTICE",
    }

    for old, new in replacements.items():

        text = re.sub(
            re.escape(old),
            new,
            text,
            flags=re.IGNORECASE,
        )

    return text


# ==========================================================
# AMOUNT HELPERS
# ==========================================================

def _find_amount_near(
    text,
    patterns,
):
    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE | re.DOTALL,
        )

        if not match:
            continue

        try:
            value = match.group(1)
        except IndexError:
            continue

        amount = _clean_number(
            value
        )

        if amount is not None:
            return amount

    return None


# ==========================================================
# GSTIN
# ==========================================================

GSTIN_PATTERN = (
    r"[0-9]{2}"
    r"[A-Z]{5}"
    r"[0-9]{4}"
    r"[A-Z]"
    r"[1-9A-Z]"
    r"Z"
    r"[0-9A-Z]"
)


def _find_gstin(text):

    text_upper = (
        text or ""
    ).upper()

    # ------------------------------------------------------
    # Strong labelled patterns
    # ------------------------------------------------------

    patterns = [

        rf"\bGSTIN\b"
        rf"\s*(?:NO\.?|NUMBER)?"
        rf"\s*[:\-]?\s*"
        rf"({GSTIN_PATTERN})",

        rf"\bGSTIN\s+OF\s+"
        rf"(?:THE\s+)?"
        rf"(?:NOTICEE|TAXPAYER|"
        rf"REGISTERED\s+PERSON)"
        rf"\s*[:\-]?\s*"
        rf"({GSTIN_PATTERN})",

        rf"\bGST\s*IN\b"
        rf"\s*[:\-]?\s*"
        rf"({GSTIN_PATTERN})",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text_upper,
            re.IGNORECASE,
        )

        if match:
            return (
                match.group(1)
                .upper()
            )

    # ------------------------------------------------------
    # Search near noticee/taxpayer/entity
    # ------------------------------------------------------

    for keyword in [
        "NOTICEE",
        "TAXPAYER",
        "REGISTERED PERSON",
        "TAXABLE PERSON",
        "PROPRIETOR",
    ]:

        match = re.search(
            rf"{keyword}.{{0,1500}}?"
            rf"({GSTIN_PATTERN})",
            text_upper,
            re.IGNORECASE | re.DOTALL,
        )

        if match:
            return (
                match.group(1)
                .upper()
            )

    # ------------------------------------------------------
    # Search all GSTINs
    # ------------------------------------------------------

    gstins = re.findall(
        GSTIN_PATTERN,
        text_upper,
    )

    gstins = _unique(
        [
            value.upper()
            for value in gstins
        ]
    )

    if len(gstins) == 1:
        return gstins[0]

    # Prefer GSTIN appearing near
    # noticee/taxpayer before tables.
    if gstins:

        for gstin in gstins:

            position = text_upper.find(
                gstin
            )

            if position < 12000:
                return gstin

    return None


# ==========================================================
# PAN
# ==========================================================

def _find_pan(text):

    pattern = (
        r"\b"
        r"[A-Z]{5}"
        r"[0-9]{4}"
        r"[A-Z]"
        r"\b"
    )

    # Strong PAN labels first

    labelled_patterns = [

        rf"\bPAN\b"
        rf"\s*(?:NO\.?|NUMBER)?"
        rf"\s*[:\-]?\s*"
        rf"({pattern})",

        rf"\bPAN\s*[:\-]\s*"
        rf"({pattern})",
    ]

    for item in labelled_patterns:

        match = re.search(
            item,
            text or "",
            re.IGNORECASE,
        )

        if match:
            return (
                match.group(1)
                .upper()
            )

    return None


# ==========================================================
# TAXPAYER / LEGAL NAME
# ==========================================================

def _clean_person_name(value):

    value = _clean_line(
        value
    )

    if not value:
        return None

    # Remove common trailing fields
    value = re.split(
        r"\b(?:GSTIN|PAN|ADDRESS|"
        r"PERIOD|DATE|TAX|DEMAND|"
        r"NOTICE|SCN|REFERENCE)\b",
        value,
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0]

    value = _clean_line(
        value
    )

    if not value:
        return None

    # Avoid returning obvious labels
    if value.upper() in {
        "NOTICEE",
        "TAXPAYER",
        "REGISTERED PERSON",
        "NAME",
    }:
        return None

    if len(value) < 3:
        return None

    if len(value) > 180:
        return None

    return value


def _find_taxpayer_name(
    text,
    gstin=None,
):

    text = text or ""

    # ------------------------------------------------------
    # 1. STRONG SCN HEADER PATTERN
    #
    # Example:
    # M/s Jagdamba Singh (GSTIN 07ANXPS5012J2ZF)
    # ------------------------------------------------------

    if gstin:

        pattern = (
            r"(M/s\.?\s+"
            r"[A-Za-z][A-Za-z0-9&.,'()\- ]{2,120}?)"
            r"\s*\(\s*GSTIN\s*"
            + re.escape(gstin)
            + r"\s*\)"
        )

        match = re.search(
            pattern,
            text,
            re.IGNORECASE,
        )

        if match:

            name = _clean_line(
                match.group(1)
            )

            if name:
                return name

    # ------------------------------------------------------
    # 2. EXPLICIT NAME LABELS
    # ------------------------------------------------------

    patterns = [

        r"Name\s+of\s+the\s+Noticee"
        r"\s*[:\-]?\s*([^\n\r]+)",

        r"Name\s+of\s+Noticee"
        r"\s*[:\-]?\s*([^\n\r]+)",

        r"Name\s+of\s+Taxpayer"
        r"\s*[:\-]?\s*([^\n\r]+)",

        r"Taxpayer\s+Name"
        r"\s*[:\-]?\s*([^\n\r]+)",

        r"Legal\s+Name\s+of\s+Business"
        r"\s*[:\-]?\s*([^\n\r]+)",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE,
        )

        if match:

            name = _clean_person_name(
                match.group(1)
            )

            if name:
                return name

    # ------------------------------------------------------
    # 3. PROPRIETOR
    #
    # Example:
    # Sh. Jagdamba Singh, the Proprietor
    # ------------------------------------------------------

    patterns = [

        r"(?:Sh\.?|Shri|Mr\.?)\s+"
        r"([A-Za-z][A-Za-z .'-]{2,100})"
        r"\s*,?\s*"
        r"(?:the\s+)?Propre?itor\b",

        r"(?:Sh\.?|Shri|Mr\.?)\s+"
        r"([A-Za-z][A-Za-z .'-]{2,100})"
        r"\s*,?\s*"
        r"Proprietor\b",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE,
        )

        if match:

            name = _clean_person_name(
                match.group(1)
            )

            if name:
                return (
                    "M/s "
                    + name
                    if not name.lower().startswith("m/s")
                    else name
                )

    # ------------------------------------------------------
    # 4. NEVER USE BROAD SCN SENTENCE FALLBACK
    #
    # This was causing:
    # Taxpayer = "Invoic"
    #
    # Do not guess taxpayer names from arbitrary text.
    # ------------------------------------------------------

    return None


# ==========================================================
# NOTICE NUMBER
# ==========================================================

def _find_notice_number(text):

    patterns = [

        r"\bSCN\s*(?:No\.?|Number)"
        r"\s*[:\-]?\s*"
        r"([A-Za-z0-9./\-_ ]{3,60})",

        r"\bNotice\s*(?:No\.?|Number)"
        r"\s*[:\-]?\s*"
        r"([A-Za-z0-9./\-_ ]{3,60})",

        r"\bReference\s*(?:No\.?|Number)"
        r"\s*[:\-]?\s*"
        r"([A-Za-z0-9./\-_ ]{3,80})",

        r"\bDIN\b"
        r"\s*[:\-]?\s*"
        r"([A-Za-z0-9./\-_]{5,100})",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text or "",
            re.IGNORECASE,
        )

        if not match:
            continue

        value = _clean_line(
            match.group(1)
        )

        if not value:
            continue

        # Stop accidental capture
        value = re.split(
            r"\b(?:Date|GSTIN|PAN|"
            r"Subject|Taxpayer|Noticee)\b",
            value,
            maxsplit=1,
            flags=re.IGNORECASE,
        )[0]

        value = _clean_line(
            value
        )

        if value:
            return value

    # ------------------------------------------------------
    # OCR fallback for standard
    # 203/2025-26 style numbers
    # ------------------------------------------------------

    match = re.search(
        r"\b"
        r"([0-9]{1,6})"
        r"\s*/\s*"
        r"(20[0-9]{2})"
        r"\s*-\s*"
        r"([0-9]{2})"
        r"\b",
        text or "",
        re.IGNORECASE,
    )

    if match:

        return (
            f"{match.group(1)}/"
            f"{match.group(2)}-"
            f"{match.group(3)}"
        )

    return None


# ==========================================================
# DOCUMENT TYPE
# ==========================================================

def _find_document_type(text):

    text = text or ""

    if re.search(
        r"FORM\s+GST\s+DRC\s*[-–—]?\s*01A\b",
        text,
        re.IGNORECASE,
    ):
        return "DRC-01A"

    if re.search(
        r"FORM\s+GST\s+DRC\s*[-–—]?\s*01\b",
        text,
        re.IGNORECASE,
    ):
        return "SCN"

    if re.search(
        r"SHOW\s+CAUSE\s+NOTICE",
        text,
        re.IGNORECASE,
    ):
        return "SCN"

    if re.search(
        r"\bSCN\b",
        text,
        re.IGNORECASE,
    ):
        return "SCN"

    if re.search(
        r"ORDER\s+IN\s+ORIGINAL|\bOIO\b",
        text,
        re.IGNORECASE,
    ):
        return "OIO"

    if re.search(
        r"APPEAL",
        text,
        re.IGNORECASE,
    ):
        return "APPEAL"

    return None


# ==========================================================
# SECTION
# ==========================================================

SECTION_PATTERN = (
    r"Section\s+"
    r"(\d+[A-Za-z]?"
    r"(?:\([0-9A-Za-z]+\))?)"
)


def _find_sections(text):

    matches = re.findall(
        SECTION_PATTERN,
        text or "",
        re.IGNORECASE,
    )

    sections = []

    for value in matches:

        value = re.sub(
            r"\s+",
            "",
            value,
        )

        section = (
            "Section "
            + value
        )

        if section not in sections:
            sections.append(
                section
            )

    return sections


def _find_section(text):

    sections = _find_sections(
        text
    )

    if not sections:
        return None

    for section in sections:

        if section.lower() == (
            "section 74(1)"
        ).lower():

            return section

    return sections[0]


# ==========================================================
# FINANCIAL YEARS
# ==========================================================

def _find_financial_years(text):

    years = re.findall(
        r"\b20\d{2}\s*-\s*\d{2}\b",
        text or "",
    )

    result = []

    for year in years:

        year = re.sub(
            r"\s+",
            "",
            year,
        )

        if year not in result:
            result.append(
                year
            )

    return result


def _find_financial_year(text):

    years = _find_financial_years(
        text
    )

    if not years:
        return None

    years = sorted(
        years,
        key=lambda x: int(
            x[:4]
        ),
    )

    if len(years) >= 2:

        return (
            f"{years[0]} to "
            f"{years[-1]}"
        )

    return years[0]


def _find_tax_period(text):

    years = _find_financial_years(
        text
    )

    if not years:
        return None

    years = sorted(
        years,
        key=lambda x: int(
            x[:4]
        ),
    )

    return ", ".join(
        years
    )


# ==========================================================
# TAX / INTEREST / PENALTY
# ==========================================================

def _find_total_itc(text):

    text = text or ""

    patterns = [

        # Table H / cancelled supplier ITC
        r"total\s+ITC\s+of\s+"
        r"(?:Rs\.?|₹)?\s*"
        r"([0-9][0-9,]*(?:\.[0-9]+)?)"
        r"\s*[-/]?\s*has\s+been\s+availed",

        # "total ITC ... Rs. 7,28,784"
        r"total\s+ITC"
        r".{0,250}?"
        r"(?:Rs\.?|₹)"
        r"\s*"
        r"([0-9][0-9,]*(?:\.[0-9]+)?)",

        # Existing generic form
        r"total\s+inadmissible\s+ITC"
        r".{0,800}?"
        r"(?:Rs\.?|₹)"
        r"\s*"
        r"([0-9][0-9,]*(?:\.[0-9]+)?)",

        r"inadmissible\s+ITC"
        r".{0,500}?"
        r"(?:Rs\.?|₹)"
        r"\s*"
        r"([0-9][0-9,]*(?:\.[0-9]+)?)",
    ]

    return _find_amount_near(
        text,
        patterns,
    )




def _find_interest(text):

    text = text or ""

    # Only extract an explicit monetary interest amount.
    # "applicable interest" without a number must remain None.

    patterns = [

        r"interest\s+"
        r"(?:payable|demanded|amount|liability)"
        r"\s*(?:of\s*)?"
        r"[:\-]?\s*"
        r"(?:Rs\.?|₹)"
        r"\s*"
        r"([0-9][0-9,]*(?:\.[0-9]+)?)",

        r"interest\s*[:\-]\s*"
        r"(?:Rs\.?|₹)"
        r"\s*"
        r"([0-9][0-9,]*(?:\.[0-9]+)?)",

        r"(?:Rs\.?|₹)"
        r"\s*"
        r"([0-9][0-9,]*(?:\.[0-9]+)?)"
        r"\s*(?:towards|for)"
        r"\s+interest\b",
    ]

    return _find_amount_near(
        text,
        patterns,
    )




def _find_penalty(text):

    text = text or ""

    patterns = [

        r"penalty\s+"
        r"(?:amount|payable|demanded|liability)"
        r"\s*(?:of\s*)?"
        r"[:\-]?\s*"
        r"(?:Rs\.?|₹)"
        r"\s*"
        r"([0-9][0-9,]*(?:\.[0-9]+)?)",

        r"penalty\s*[:\-]\s*"
        r"(?:Rs\.?|₹)"
        r"\s*"
        r"([0-9][0-9,]*(?:\.[0-9]+)?)",
    ]

    return _find_amount_near(
        text,
        patterns,
    )




def _find_tax_amount(text):

    # Detailed tax-demand extraction belongs to
    # demand_extractor.py.
    #
    # This SCN contains multiple tax/ITC demands:
    # RCM, outward supply, excess ITC and cancelled supplier ITC.
    #
    # Returning None here prevents accidental selection of
    # an unrelated amount from the document.

    return None




# ==========================================================
# DATE
# ==========================================================

def _find_date(text):

    patterns = [

        r"\b\d{2}[./-]\d{2}[./-]\d{4}\b",

        r"\b\d{2}\s*[./-]\s*"
        r"\d{2}\s*[./-]\s*"
        r"\d{4}\b",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text or "",
        )

        if match:

            return re.sub(
                r"\s+",
                "",
                match.group(0),
            )

    return None


def _find_scn_date(text):

    text = text or ""

    # ------------------------------------------------------
    # Explicit header date
    #
    # OCR example:
    # C. No. ... Date: .07.2024
    # SHOW CAUSE NOTICE No. 73/2024
    # ------------------------------------------------------

    patterns = [

        r"(?:Date|Dated)"
        r"\s*[:\-]?\s*"
        r"\.?\s*"
        r"(\d{2}[./-]\d{4})",

        r"(?:Date|Dated)"
        r"\s*[:\-]?\s*"
        r"\.?\s*"
        r"(\d{2})[./-](\d{4})",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE,
        )

        if match:

            if match.lastindex == 2:

                return (
                    match.group(1)
                    + "."
                    + match.group(2)
                )

            return (
                match.group(1)
                .replace(" ", "")
                .replace("/", ".")
                .replace("-", ".")
            )

    return None



# ==========================================================
# SUPPLIER / VENDOR
# ==========================================================

# ==========================================================
# SUPPLIER / VENDOR
# ==========================================================

def _find_vendor(text):

    text = text or ""

    patterns = [

        # --------------------------------------------------
        # invoices issued by M/s COMPANY (GSTIN ...)
        # --------------------------------------------------

        r"invoices?\s+issued\s+by\s+"
        r"(M/s\s+.*?)"
        r"\s*\(\s*GSTIN\s*"
        r"[0-9A-Z]{15}"
        r"\s*\)",

        # --------------------------------------------------
        # supplier ... M/s COMPANY (GSTIN ...)
        # --------------------------------------------------

        r"supplier"
        r".{0,150}?"
        r"(M/s\s+.*?)"
        r"\s*\(\s*GSTIN\s*"
        r"[0-9A-Z]{15}"
        r"\s*\)",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE | re.DOTALL,
        )

        if match:

            value = match.group(1)

            value = re.sub(
                r"\s+",
                " ",
                value,
            ).strip()

            return value

    return None


def _find_vendor_gstin(text):

    text = text or ""

    patterns = [

        r"invoices?\s+issued\s+by\s+"
        r"M/s\s+.*?"
        r"\(\s*GSTIN\s*"
        r"([0-9A-Z]{15})"
        r"\s*\)",

        r"supplier"
        r".{0,150}?"
        r"M/s\s+.*?"
        r"\(\s*GSTIN\s*"
        r"([0-9A-Z]{15})"
        r"\s*\)",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE | re.DOTALL,
        )

        if match:
            return match.group(1).upper()

    return None




# ==========================================================
# AUTHORITY
# ==========================================================

def _find_authority(text):

    patterns = [

        r"(Office\s+of\s+the\s+"
        r"(?:Principal\s+Commissioner|"
        r"Commissioner|Additional\s+Commissioner)"
        r".{0,300}?"
        r"(?:GST|CGST|Delhi|"
        r"North|South|East|West)[^\n]{0,150})",

        r"((?:Principal\s+Commissioner|"
        r"Commissioner|Additional\s+Commissioner)"
        r"[^\n]{0,200})",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text or "",
            re.IGNORECASE | re.DOTALL,
        )

        if match:

            value = _clean_line(
                match.group(1)
            )

            if value:
                return value

    return None


# ==========================================================
# ISSUE
# ==========================================================

def _find_issue(text):

    if re.search(
        r"wrong\s+availment"
        r".{0,300}?"
        r"input\s+tax\s+credit",
        text or "",
        re.IGNORECASE | re.DOTALL,
    ):
        return (
            "Wrong availment of "
            "Input Tax Credit"
        )

    if re.search(
        r"ineligible"
        r".{0,300}?"
        r"input\s+tax\s+credit",
        text or "",
        re.IGNORECASE | re.DOTALL,
    ):
        return (
            "Ineligible Input Tax Credit"
        )

    if re.search(
        r"input\s+tax\s+credit",
        text or "",
        re.IGNORECASE,
    ):
        return (
            "Input Tax Credit"
        )

    return None


# ==========================================================
# MAIN EXTRACTOR
# ==========================================================

def extract_gst_metadata(
    text: str
):

    text = _normalise_ocr(
        _clean_text(text)
    )

    gstin = _find_gstin(
        text
    )

    pan = _find_pan(
        text
    )

    taxpayer_name = (
        _find_taxpayer_name(
            text,
            gstin,
        )
    )

    notice_number = (
        _find_notice_number(
            text
        )
    )

    document_type = (
        _find_document_type(
            text
        )
    )

    section = _find_section(
        text
    )

    sections = _find_sections(
        text
    )

    financial_year = (
        _find_financial_year(
            text
        )
    )

    tax_period = (
        _find_tax_period(
            text
        )
    )

    tax_amount = (
        _find_tax_amount(
            text
        )
    )

    total_itc = (
        _find_total_itc(
            text
        )
    )

    interest = (
        _find_interest(
            text
        )
    )

    penalty = (
        _find_penalty(
            text
        )
    )

    scn_date = (
        _find_scn_date(
            text
        )
    )

    authority = (
        _find_authority(
            text
        )
    )

    vendor = _find_vendor(
        text
    )

    vendor_gstin = _find_vendor_gstin(
        text
    )

    issue = _find_issue(
        text
    )

    issue_category = None

    if re.search(
        r"\bITC\b|"
        r"Input\s+Tax\s+Credit",
        text,
        re.IGNORECASE,
    ):
        issue_category = "ITC"

    # ------------------------------------------------------
    # RETURN
    # ------------------------------------------------------

    return {

        "gstin":
            gstin,

        "pan":
            pan,

        "taxpayer_name":
            taxpayer_name,

        "notice_number":
            notice_number,

        "document_type":
            document_type,

        "section":
            section,

        "financial_year":
            financial_year,

        "tax_period":
            tax_period,

        "tax_amount":
            tax_amount,

        "total_inadmissible_itc":
            total_itc,

        "interest":
            interest,

        "penalty":
            penalty,

        "date":
            scn_date,

        "scn_date":
            scn_date,

        "authority":
            authority,

        "vendor":
            vendor,

        "vendor_gstin":
            vendor_gstin,

        "issue":
            issue,

        "issue_category":
            issue_category,

        "sections":
            sections,
    }
