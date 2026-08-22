import re
from typing import Any, Dict, List, Optional


# ==========================================================
# BASIC HELPERS
# ==========================================================

AMOUNT_PATTERN = (
    r"(?:₹|Rs\.?|INR)?\s*"
    r"([0-9][0-9,]*(?:\.[0-9]+)?)"
)


def _amount(value: str) -> Optional[float]:

    if not value:
        return None

    try:
        value = (
            str(value)
            .replace(",", "")
            .replace("/-", "")
            .strip()
        )

        return float(value)

    except (ValueError, TypeError):
        return None


def _clean_text(value: str) -> str:

    return re.sub(
        r"\s+",
        " ",
        value or "",
    ).strip()


def _unique_items(items):

    result = []
    seen = set()

    for item in items:

        key = (
            item.get("type"),
            item.get("amount"),
            item.get("tax_period"),
            item.get("section"),
            item.get("table_reference"),
        )

        if key in seen:
            continue

        seen.add(key)
        result.append(item)

    return result


def _extract_section(text: str):

    match = re.search(
        r"\bSection\s+"
        r"(\d+[A-Za-z]?"
        r"(?:\(\d+\))?)",
        text or "",
        re.IGNORECASE,
    )

    if match:
        return "Section " + match.group(1)

    return None


def _extract_amount(text: str):

    match = re.search(
        r"(?:₹|Rs\.?|INR)\s*"
        r"([0-9][0-9,]*(?:\.[0-9]+)?)",
        text or "",
        re.IGNORECASE,
    )

    if not match:
        return None

    return _amount(
        match.group(1)
    )


# ==========================================================
# PARA 23 DEMAND EXTRACTION
# ==========================================================

def _find_para_23(text: str):

    text = text or ""

    # ------------------------------------------------------
    # Locate the beginning of Para 23.
    #
    # OCR can contain different spacing/newlines between:
    # 23. Now, therefore
    # ------------------------------------------------------

    start_match = re.search(
        r"(?:^|\n)"
        r"\s*23\.\s*"
        r"Now\s*,?\s*"
        r"therefore\b",
        text,
        re.IGNORECASE,
    )

    if not start_match:

        start_match = re.search(
            r"\b23\.\s*Now\b",
            text,
            re.IGNORECASE,
        )

    if not start_match:
        return None

    start = start_match.start()

    # ------------------------------------------------------
    # Locate Para 24.
    #
    # Do NOT use a short fixed character window.
    # This allows the complete Para 23 to survive,
    # including (i), (ii), (iii), (iv), (v), (vi), (vii).
    # ------------------------------------------------------

    end_match = re.search(
        r"(?:^|\n)"
        r"\s*24\.\s*"
        r"(?:Now\s*,?\s*therefore\b|)",
        text[start:],
        re.IGNORECASE,
    )

    if end_match:

        end = (
            start
            + end_match.start()
        )

    else:

        # Fallback: keep enough text for long SCNs.
        end = min(
            len(text),
            start + 20000,
        )

    para_23 = text[
        start:end
    ]

    # ------------------------------------------------------
    # Normalize only whitespace.
    #
    # IMPORTANT:
    # Do NOT remove Roman-numbered clauses such as:
    # (i), (ii), (iii), (iv), (v), (vi), (vii)
    # ------------------------------------------------------

    para_23 = re.sub(
        r"[ \t]+",
        " ",
        para_23,
    )

    para_23 = re.sub(
        r"\n{3,}",
        "\n\n",
        para_23,
    )

    return para_23


# ==========================================================
# SINGLE DEMAND BLOCK
# ==========================================================

def _build_demand_item(
    number,
    block,
):

    block = _clean_text(
        block
    )

    amount = _extract_amount(
        block
    )

    if amount is None:
        return None

    section = _extract_section(
        block
    )

    # ------------------------------------------------------
    # RCM
    # ------------------------------------------------------

    if re.search(
        r"reverse\s+charge\s+mechanism",
        block,
        re.IGNORECASE,
    ):

        demand_type = "tax"

        category = "RCM"

        description = (
            "GST not paid under "
            "Reverse Charge Mechanism"
        )

        table_reference = "Table E"

    # ------------------------------------------------------
    # OUTWARD SUPPLY
    # ------------------------------------------------------

    elif re.search(
        r"outward\s+supply",
        block,
        re.IGNORECASE,
    ):

        demand_type = "tax"

        category = "OUTWARD_SUPPLY"

        description = (
            "GST not paid on "
            "outward supply"
        )

        table_reference = "Table F"

    # ------------------------------------------------------
    # EXCESS ITC
    # ------------------------------------------------------

    elif re.search(
        r"Input\s+Tax\s+Credit"
        r".{0,250}?"
        r"difference\s+between"
        r".{0,250}?"
        r"GSTR-?2A"
        r".{0,250}?"
        r"GSTR-?3B",
        block,
        re.IGNORECASE,
    ):

        demand_type = "itc"

        category = "EXCESS_ITC"

        description = (
            "Input Tax Credit wrongly "
            "availed and utilized in excess"
        )

        table_reference = "Table G"

    # ------------------------------------------------------
    # CANCELLED SUPPLIER ITC
    # ------------------------------------------------------

    elif re.search(
        r"Input\s+Tax\s+Credit",
        block,
        re.IGNORECASE,
    ) and re.search(
        r"cancellation\s+of\s+registration",
        block,
        re.IGNORECASE,
    ):

        demand_type = "itc"

        category = "CANCELLED_SUPPLIER_ITC"

        description = (
            "ITC availed on invoices "
            "issued after cancellation "
            "of supplier registration"
        )

        table_reference = "Table H"

    else:

        return None

    # ------------------------------------------------------
    # ACT
    # ------------------------------------------------------

    if re.search(
        r"IGST\s+Act",
        block,
        re.IGNORECASE,
    ):
        act = "CGST + IGST"

    elif re.search(
        r"CGST\s+Act",
        block,
        re.IGNORECASE,
    ):
        act = "CGST"

    else:
        act = None

    # ------------------------------------------------------
    # TAX PERIOD
    # ------------------------------------------------------

    tax_period = None

    period_match = re.search(
        r"\b"
        r"(20\d{2}-\d{2})"
        r"\b",
        block,
    )

    if period_match:
        tax_period = (
            period_match.group(1)
        )

    return {
        "type": demand_type,
        "category": category,
        "description": description,
        "amount": amount,
        "tax_period": tax_period,
        "act": act,
        "section": section,
        "table_reference": table_reference,
        "demand_number": number,
        # Penalty is handled separately through Para 23
        # items (ii), (iv), and (vi). Do NOT detect the
        # word "Penalty" inside the tax block because the
        # same block may contain the linked penalty clause.
        "penalty_proposed": False,

        "interest_proposed": bool(
            re.search(
                r"applicable\s+Interest"
                r"|Interest\s+u/s\s+50",
                block,
                re.IGNORECASE,
            )
        ),
        "source_text": block,
    }


# ==========================================================
# PARA 23 LINKED PENALTIES
# ==========================================================

def extract_penalty_proposals(
    text: str,
) -> List[Dict[str, Any]]:

    text = text or ""

    para_23 = _find_para_23(text)

    if not para_23:
        return []

    penalties = []

    # ------------------------------------------------------
    # OCR-SAFE PENALTY CLAUSE DEFINITIONS
    #
    # OCR may produce:
    #
    # (ii) Penalty
    # ii) Penalty
    #
    # Therefore the opening "(" is OPTIONAL.
    #
    # Links:
    # ii  -> i
    # iv  -> iii
    # vi  -> v
    # ------------------------------------------------------

    clauses = [
        {
            "number": "ii",
            "linked": "i",
            "start": r"\(?\s*ii\s*\)",
            "end": r"\(\s*iii\s*\)",
        },
        {
            "number": "iv",
            "linked": "iii",
            "start": r"\(?\s*iv\s*\)",
            "end": r"\(\s*v\s*\)",
        },
        {
            "number": "vi",
            "linked": "v",
            "start": r"\(?\s*vi\s*\)",
            "end": r"\(\s*vii\s*\)",
        },
    ]

    for clause in clauses:

        pattern = (
            clause["start"]
            + r"\s*(.*?)"
            + r"(?="
            + clause["end"]
            + r"|$)"
        )

        match = re.search(
            pattern,
            para_23,
            re.IGNORECASE | re.DOTALL,
        )

        if not match:
            continue

        block = _clean_text(
            match.group(1)
        )

        if not block:
            continue

        # --------------------------------------------------
        # Confirm actual penalty clause.
        # --------------------------------------------------

        if not re.search(
            r"\bPenalty\b",
            block,
            re.IGNORECASE,
        ):
            continue

        if not re.search(
            r"equivalent\s+to",
            block,
            re.IGNORECASE,
        ):
            continue

        penalties.append(
            {
                "penalty_number":
                    clause["number"],

                "linked_demand_number":
                    clause["linked"],

                "type":
                    "penalty",

                "category":
                    "EQUIVALENT_PENALTY",

                # Do not invent numeric amount.
                "amount":
                    None,

                "amount_source":
                    (
                        "Equivalent to demand "
                        f"({clause['linked']})"
                    ),

                "section":
                    "Section 122(2)",

                "act":
                    "CGST",

                "table_reference":
                    None,

                "source_text":
                    block,
            }
        )

    return penalties


# ==========================================================
# PARA 23 STRUCTURED DEMANDS
# ==========================================================

def extract_demand_items(
    text: str,
) -> List[Dict[str, Any]]:

    text = text or ""

    para_23 = _find_para_23(
        text
    )

    if not para_23:
        return []

    items = []

    # ------------------------------------------------------
    # Demand (i)
    # ------------------------------------------------------

    patterns = [

        (
            "i",
            r"\(i\)"
            r"(.*?)(?=\bii\)|\(ii\))"
        ),

        (
            "iii",
            r"\(iii\)"
            r"(.*?)(?=\biv\)|\(iv\))"
        ),

        (
            "v",
            r"\(v\)"
            r"(.*?)(?=\bvi\)|\(vi\))"
        ),

        (
            "vii",
            r"\(vii\)"
            r"(.*?)(?=\b24\.)"
        ),
    ]

    for number, pattern in patterns:

        match = re.search(
            pattern,
            para_23,
            re.IGNORECASE | re.DOTALL,
        )

        if not match:
            continue

        block = match.group(1)

        item = _build_demand_item(
            number,
            block,
        )

        if item:
            items.append(
                item
            )

    return _unique_items(
        items
    )


# ==========================================================
# PERIOD-WISE TABLE F
# ==========================================================

def extract_table_f_periods(
    text: str,
) -> List[Dict[str, Any]]:

    text = text or ""

    match = re.search(
        r"Table\s+F"
        r".{0,3000}?"
        r"Difference\s+b/w\s+ITC",
        text,
        re.IGNORECASE | re.DOTALL,
    )

    if not match:
        return []

    block = match.group(0)

    rows = []

    pattern = (
        r"\b"
        r"(18-19|19-20|20-21|21-22)"
        r"\s+"
        r"([0-9][0-9,]*)"
        r"/?-?\s*"
        r"([0-9][0-9,]*)"
        r"/?-?"
    )

    for row in re.finditer(
        pattern,
        block,
        re.IGNORECASE,
    ):

        tax_period = row.group(1)

        supply_value = _amount(
            row.group(2)
        )

        tax = _amount(
            row.group(3)
        )

        if tax is None:
            continue

        rows.append(
            {
                "tax_period": tax_period,
                "act": "CGST",
                "section": "Section 74(1)",
                "tax": tax,
                "interest": None,
                "penalty": None,
                "supply_value": supply_value,
                "table_reference": "Table F",
            }
        )

    return rows


# ==========================================================
# PERIOD-WISE TABLE G
# ==========================================================

def extract_table_g_periods(
    text: str,
) -> List[Dict[str, Any]]:

    text = text or ""

    match = re.search(
        r"Table\s+G"
        r".{0,2500}?"
        r"Thus in view",
        text,
        re.IGNORECASE | re.DOTALL,
    )

    if not match:
        return []

    block = match.group(0)

    rows = []

    pattern = (
        r"\b"
        r"(20\d{2}-\d{2})"
        r"\s+"
        r"([0-9][0-9,]*)"
        r"/?-?\s+"
        r"([0-9][0-9,]*)"
        r"/?-?\s+"
        r"([0-9][0-9,]*)"
        r"/?-?"
    )

    for row in re.finditer(
        pattern,
        block,
        re.IGNORECASE,
    ):

        tax_period = row.group(1)

        gstr2a = _amount(
            row.group(2)
        )

        gstr3b = _amount(
            row.group(3)
        )

        excess_itc = _amount(
            row.group(4)
        )

        if excess_itc is None:
            continue

        rows.append(
            {
                "tax_period": tax_period,
                "act": "CGST",
                "section": "Section 16",
                "tax": excess_itc,
                "interest": None,
                "penalty": None,
                "gstr2a": gstr2a,
                "gstr3b": gstr3b,
                "excess_itc": excess_itc,
                "table_reference": "Table G",
            }
        )

    return rows


# ==========================================================
# PERIOD-WISE DEMANDS
# ==========================================================

def extract_period_wise_demands(
    text: str,
) -> List[Dict[str, Any]]:

    rows = []

    rows.extend(
        extract_table_f_periods(
            text
        )
    )

    rows.extend(
        extract_table_g_periods(
            text
        )
    )

    return rows


# ==========================================================
# DEMAND SUMMARY
# ==========================================================

def extract_demand_summary(
    text: str,
) -> Dict[str, Any]:

    items = extract_demand_items(
        text
    )

    tax_total = 0.0
    interest_total = 0.0

    for item in items:

        amount = (
            item.get("amount")
            or 0.0
        )

        if item.get("type") in (
            "tax",
            "itc",
        ):
            tax_total += amount

    # ------------------------------------------------------
    # Penalties are linked proposals.
    #
    # Para 23(ii), (iv), and (vi) say the penalty is
    # equivalent to the corresponding demand.
    #
    # We keep these proposals separately and DO NOT add
    # them again to total_demand.
    # ------------------------------------------------------

    penalty_proposals = (
        extract_penalty_proposals(
            text
        )
    )

    penalty_total = None

    total_demand = (
        tax_total
        + interest_total
    )

    return {
        "items": items,

        "penalty_proposals":
            penalty_proposals,

        "tax_total":
            tax_total,

        "interest_total":
            interest_total,

        "penalty_total":
            penalty_total,

        "total_demand":
            total_demand,
    }


# ==========================================================
# BACKWARD COMPATIBILITY
# ==========================================================

def extract_amounts(
    text: str,
) -> List[float]:

    values = []

    for match in re.finditer(
        AMOUNT_PATTERN,
        text or "",
        re.IGNORECASE,
    ):

        amount = _amount(
            match.group(1)
        )

        if amount is not None:
            values.append(
                amount
            )

    return values


def extract_demand_summary_legacy(
    text: str,
):

    return extract_demand_summary(
        text
    )
