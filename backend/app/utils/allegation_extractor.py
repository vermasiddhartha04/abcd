import re
from typing import Any, Dict, List


SECTION_RE = re.compile(
    r"\bSection\s+\d+[A-Za-z]?"
    r"(?:\(\d+[A-Za-z]?\))?",
    re.IGNORECASE,
)


def _clean(value: str) -> str:
    return re.sub(
        r"\s+",
        " ",
        value or "",
    ).strip()


def _unique(values):
    result = []

    for value in values:
        value = _clean(value)

        if value and value not in result:
            result.append(value)

    return result


def _sections(text: str) -> List[str]:

    found = []

    for section in SECTION_RE.findall(
        text or ""
    ):

        normalized = _clean(section)

        if normalized not in found:
            found.append(normalized)

    return found


def _category_from_text(text: str) -> str:

    value = (text or "").lower()

    # ------------------------------------------------------
    # RCM
    # ------------------------------------------------------

    if (
        "reverse charge mechanism" in value
        or "reverse charge" in value
    ):
        return "RCM"

    # ------------------------------------------------------
    # Cancelled supplier ITC
    # ------------------------------------------------------

    if (
        "cancellation of registration" in value
        or "registration of supplier" in value
        or "cancelled retrospectively" in value
        or (
            "after the date of cancellation"
            in value
            and "itc" in value
        )
        or (
            "supplier after the date of cancellation"
            in value
        )
    ):
        return "CANCELLED_SUPPLIER_ITC"

    # ------------------------------------------------------
    # Excess ITC
    # ------------------------------------------------------

    if (
        "gstr-2a" in value
        and "gstr-3b" in value
    ) or (
        "excess itc" in value
        or "inadmissible excess itc" in value
    ):
        return "EXCESS_ITC"

    # ------------------------------------------------------
    # Outward supply
    # ------------------------------------------------------

    if (
        "outward supply" in value
        or "parking services" in value
        or "nil rated/exempt" in value
    ):
        return "OUTWARD_SUPPLY"

    # ------------------------------------------------------
    # Limitation / suppression
    # ------------------------------------------------------

    if (
        "wilful misstatement" in value
        or "wilfully mis-stated" in value
        or "willfully mis-stated" in value
        or "suppressed the vital facts" in value
        or "intention to evade" in value
        or "evasion of gst liabilities" in value
    ):
        return "LIMITATION_SUPPRESSION"

    return "GENERAL"


def _extract_numbered_conclusions(
    text: str,
) -> List[Dict[str, Any]]:

    """
    Extract actual taxpayer conclusions from Para 19.

    Handles:
        19(1) -> RCM
        19(2) -> OUTWARD_SUPPLY
        19(3) -> EXCESS_ITC
        19(4) -> CANCELLED_SUPPLIER_ITC

    Ignores the statutory 19(1)-style text that appears
    earlier in the document.
    """

    text = text or ""

    # ------------------------------------------------------
    # Find the actual Para 19 section.
    # ------------------------------------------------------

    para_match = re.search(
        r"(?:^|\n)"
        r"\s*19\s*"
        r"(?:\.\s*)?"
        r"(?:Conclusion|CONCLUSION)"
        r".*?"
        r"(?="
        r"\n\s*20\s+From\s+the\s+foregoing"
        r"|\Z"
        r")",
        text,
        re.IGNORECASE | re.DOTALL,
    )

    if para_match:
        para_19 = para_match.group(0)
    else:
        # Fallback: locate the first actual taxpayer
        # conclusion containing "M/s JS".
        taxpayer_match = re.search(
            r"(?:^|\n)"
            r"\s*19\s*\(\s*1\s*\)"
            r"\s*M/s\s+JS\b",
            text,
            re.IGNORECASE,
        )

        if not taxpayer_match:
            return []

        start_pos = taxpayer_match.start()

        end_match = re.search(
            r"\n\s*20\s+From\s+the\s+foregoing",
            text[start_pos:],
            re.IGNORECASE,
        )

        if end_match:
            end_pos = (
                start_pos
                + end_match.start()
            )
        else:
            end_pos = min(
                len(text),
                start_pos + 15000,
            )

        para_19 = text[
            start_pos:end_pos
        ]

    # ------------------------------------------------------
    # Extract 19(1) through 19(4).
    # ------------------------------------------------------

    pattern = re.compile(
        r"(?P<number>"
        r"19\s*\(\s*[1-4]\s*\)"
        r")"
        r"\s*",
        re.IGNORECASE,
    )

    matches = list(
        pattern.finditer(para_19)
    )

    allegations = []

    for index, match in enumerate(matches):

        # Extract the inner conclusion number.
        #
        # Example:
        # 19(1) -> 1
        # 19(2) -> 2
        # 19(3) -> 3
        # 19(4) -> 4
        #
        # Then rebuild the complete number as 19(1), etc.

        number_match = re.search(
            r"\(\s*([1-4])\s*\)",
            match.group("number"),
        )

        if not number_match:
            continue

        number = match.group("number")

        # Normalize OCR spacing only.
        # match.group("number") already contains:
        # 19(1), 19(2), 19(3), or 19(4).
        number = re.sub(
            r"\s+",
            "",
            number,
        )

        # Normalize any accidental nested value from an
        # earlier extractor version.
        number = re.sub(
            r"^19\(19\(([1-4])\)\)$",
            r"19(\1)",
            number,
        )

        start_pos = match.start()

        if index + 1 < len(matches):
            end_pos = matches[
                index + 1
            ].start()
        else:
            end_pos = len(para_19)

        block = _clean(
            para_19[
                start_pos:end_pos
            ]
        )

        if len(block) < 30:
            continue

        # --------------------------------------------------
        # Ignore statutory wording.
        #
        # Actual allegation begins with M/s JS.
        # --------------------------------------------------

        if not re.search(
            r"\bM/s\s+JS\b"
            r"|\bM/s\s+Jagdamba\s+Singh\b",
            block,
            re.IGNORECASE,
        ):
            continue

        category = _category_from_text(
            block
        )

        allegations.append(
            {
                "number":
                    number,

                "title":
                    f"Conclusion {number}",

                "category":
                    category,

                "text":
                    block,

                "sections":
                    _sections(block),
            }
        )

    return allegations


def _extract_para_18_itc(
    text: str,
) -> List[Dict[str, Any]]:

    """
    Extract the cancelled-supplier ITC allegation
    from Para 18.

    This is deliberately limited to the paragraph
    containing the supplier cancellation allegation.
    """

    text = text or ""

    match = re.search(
        r"(?:^|\n)"
        r"\s*18\.\s*"
        r"(.*?)(?="
        r"\n\s*(?:19\.|LEGAL\s+PROVISIONS)"
        r")",
        text,
        re.IGNORECASE | re.DOTALL,
    )

    if not match:
        return []

    block = _clean(
        match.group(0)
    )

    if not re.search(
        r"cancell",
        block,
        re.IGNORECASE,
    ):
        return []

    if not re.search(
        r"\bITC\b|Input\s+Tax\s+Credit",
        block,
        re.IGNORECASE,
    ):
        return []

    return [
        {
            "number": "18",
            "title": "Cancelled Supplier ITC",
            "category": "CANCELLED_SUPPLIER_ITC",
            "text": block,
            "sections": _sections(
                block
            ),
        }
    ]


def _extract_para_20_contravention(
    text: str,
) -> List[Dict[str, Any]]:

    """
    Extract Para 20 separately.

    Para 20 is a general contravention /
    suppression / wilful-misstatement allegation,
    not another individual tax demand.
    """

    text = text or ""

    match = re.search(
        r"(?:^|\n)"
        r"\s*20\s+From\s+the\s+foregoing"
        r"(.*?)(?="
        r"\n\s*21\."
        r")",
        text,
        re.IGNORECASE | re.DOTALL,
    )

    if not match:
        return []

    block = _clean(
        match.group(0)
    )

    if not block:
        return []

    return [
        {
            "number": "20",
            "title": (
                "Contravention and Grounds "
                "for invoking Section 74"
            ),
            "category": "LIMITATION_SUPPRESSION",
            "text": block,
            "sections": _sections(
                block
            ),
        }
    ]


def extract_allegations(
    text: str,
) -> List[Dict[str, Any]]:

    """
    Structured rule-based allegation extraction.

    Sources used by this extractor:

    - Para 18:
        Cancelled supplier ITC
    - Para 19(1):
        RCM
    - Para 19(2):
        Outward supply
    - Para 19(3):
        Excess ITC
    - Para 20:
        Wilful misstatement / suppression /
        Section 74 grounds

    The extractor does not invent legal conclusions.
    """

    text = text or ""

    allegations = []

    # ------------------------------------------------------
    # Para 18
    # ------------------------------------------------------

    allegations.extend(
        _extract_para_18_itc(
            text
        )
    )

    # ------------------------------------------------------
    # Para 19(1) - 19(3)
    # ------------------------------------------------------

    allegations.extend(
        _extract_numbered_conclusions(
            text
        )
    )

    # ------------------------------------------------------
    # Para 20
    # ------------------------------------------------------

    allegations.extend(
        _extract_para_20_contravention(
            text
        )
    )

    # ------------------------------------------------------
    # Final numbering
    # ------------------------------------------------------

    for index, item in enumerate(
        allegations,
        start=1,
    ):
        item["number_index"] = index

    return allegations


def extract_issue_keywords(
    text: str,
) -> List[str]:

    text = (
        text or ""
    ).lower()

    keyword_map = {

        "ITC": [
            "input tax credit",
            "itc",
        ],

        "RCM": [
            "reverse charge",
            "rcm",
        ],

        "OUTWARD_SUPPLY": [
            "outward supply",
            "short payment",
            "parking services",
        ],

        "EXCESS_ITC": [
            "gstr-2a",
            "gstr2a",
            "gstr-3b",
            "gstr3b",
            "excess itc",
        ],

        "CANCELLED_SUPPLIER_ITC": [
            "cancellation of registration",
            "cancelled retrospectively",
            "registration of supplier",
        ],

        "INTEREST": [
            "interest",
        ],

        "PENALTY": [
            "penalty",
        ],

        "LIMITATION": [
            "limitation",
            "suppression",
            "wilful misstatement",
            "wilfully mis-stated",
            "willfully mis-stated",
            "fraud",
            "intention to evade",
        ],
    }

    found = []

    for category, keywords in (
        keyword_map.items()
    ):

        if any(
            keyword in text
            for keyword in keywords
        ):
            found.append(
                category
            )

    return found
