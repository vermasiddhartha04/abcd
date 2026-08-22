import re
from typing import Any, Dict, List


def extract_tables(text: str) -> List[Dict[str, Any]]:
    """
    Lightweight OCR/text table detection.

    Keeps table-like lines without attempting to invent
    missing columns or values.
    """

    text = text or ""
    lines = text.splitlines()

    tables = []
    current = []

    for line in lines:

        stripped = line.strip()

        if not stripped:
            if len(current) >= 3:
                tables.append(
                    {
                        "rows": current[:],
                        "row_count": len(current),
                    }
                )

            current = []
            continue

        pipe_count = stripped.count("|")
        tab_count = line.count("\t")
        multi_space = bool(
            re.search(r"\s{3,}", stripped)
        )

        if pipe_count >= 1 or tab_count >= 1 or multi_space:
            current.append(
                re.sub(
                    r"\s+",
                    " ",
                    stripped,
                )
            )
        else:
            if len(current) >= 3:
                tables.append(
                    {
                        "rows": current[:],
                        "row_count": len(current),
                    }
                )

            current = []

    if len(current) >= 3:
        tables.append(
            {
                "rows": current[:],
                "row_count": len(current),
            }
        )

    return tables
