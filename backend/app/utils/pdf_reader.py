import os
import re
from typing import List

import pytesseract
from PIL import Image
from pypdf import PdfReader

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None


# ==========================================================
# TESSERACT CONFIGURATION
# ==========================================================

def configure_tesseract() -> None:
    """
    Configure Tesseract on Windows.

    If Tesseract is already available through PATH,
    no explicit configuration is required.
    """

    possible_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ]

    for path in possible_paths:

        if os.path.exists(path):

            pytesseract.pytesseract.tesseract_cmd = path

            break


configure_tesseract()


# ==========================================================
# NORMAL PDF TEXT EXTRACTION
# ==========================================================

def extract_text_with_pypdf(
    file_path: str,
) -> str:

    reader = PdfReader(file_path)

    text_parts: List[str] = []

    for page_number, page in enumerate(
        reader.pages,
        start=1,
    ):

        try:

            page_text = (
                page.extract_text()
                or ""
            )

        except Exception:

            page_text = ""

        page_text = page_text.strip()

        if page_text:

            text_parts.append(
                f"\n--- Page {page_number} ---\n"
            )

            text_parts.append(
                page_text
            )

    return "\n".join(
        text_parts
    ).strip()


# ==========================================================
# OCR EXTRACTION
# ==========================================================

def extract_text_with_ocr(
    file_path: str,
) -> str:

    if fitz is None:

        raise RuntimeError(
            "PyMuPDF is not installed. "
            "Run: pip install PyMuPDF"
        )

    document = fitz.open(
        file_path
    )

    text_parts: List[str] = []

    try:

        total_pages = len(document)

        for page_index in range(
            total_pages
        ):

            page_number = (
                page_index + 1
            )

            page = document[
                page_index
            ]

            # --------------------------------------------------
            # Render PDF page as image
            # --------------------------------------------------

            matrix = fitz.Matrix(
                2.5,
                2.5,
            )

            pixmap = page.get_pixmap(
                matrix=matrix,
                alpha=False,
            )

            image = Image.frombytes(
                "RGB",
                [
                    pixmap.width,
                    pixmap.height,
                ],
                pixmap.samples,
            )

            # --------------------------------------------------
            # OCR
            # --------------------------------------------------

            try:

                page_text = pytesseract.image_to_string(
                    image,
                    config="--psm 6",
                )

            except Exception as exc:

                print(
                    f"OCR failed on page "
                    f"{page_number}: {exc}"
                )

                page_text = ""

            page_text = (
                page_text
                or ""
            ).strip()

            if page_text:

                text_parts.append(
                    f"\n--- Page {page_number} ---\n"
                )

                text_parts.append(
                    page_text
                )

    finally:

        document.close()

    return "\n".join(
        text_parts
    ).strip()


# ==========================================================
# CLEAN OCR TEXT
# ==========================================================

def clean_extracted_text(
    text: str,
) -> str:

    if not text:

        return ""

    # Remove excessive spaces
    text = re.sub(
        r"[ \t]+",
        " ",
        text,
    )

    # Reduce excessive blank lines
    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text,
    )

    # Normalize page separators
    text = re.sub(
        r"\n---\s*Page\s+(\d+)\s*---\n",
        r"\n\n--- Page \1 ---\n",
        text,
        flags=re.IGNORECASE,
    )

    return text.strip()


# ==========================================================
# MAIN PDF TEXT EXTRACTION
# ==========================================================

def extract_text_from_pdf(
    file_path: str,
) -> str:

    if not os.path.exists(
        file_path
    ):

        raise FileNotFoundError(
            f"PDF file not found: {file_path}"
        )

    # ------------------------------------------------------
    # STEP 1
    # Try normal PDF extraction
    # ------------------------------------------------------

    print(
        "PDF TEXT EXTRACTION: "
        "Trying pypdf..."
    )

    extracted_text = (
        extract_text_with_pypdf(
            file_path
        )
    )

    extracted_text = (
        clean_extracted_text(
            extracted_text
        )
    )

    # ------------------------------------------------------
    # STEP 2
    # Check whether enough text was found
    # ------------------------------------------------------

    if len(extracted_text) >= 100:

        print(
            "PDF TEXT EXTRACTION: "
            f"Success ({len(extracted_text)} characters)"
        )

        return extracted_text

    # ------------------------------------------------------
    # STEP 3
    # OCR FALLBACK
    # ------------------------------------------------------

    print(
        "PDF TEXT EXTRACTION: "
        "Insufficient text found."
    )

    print(
        "PDF TEXT EXTRACTION: "
        "Starting OCR..."
    )

    ocr_text = (
        extract_text_with_ocr(
            file_path
        )
    )

    ocr_text = (
        clean_extracted_text(
            ocr_text
        )
    )

    # ------------------------------------------------------
    # STEP 4
    # OCR result validation
    # ------------------------------------------------------

    if len(ocr_text) < 50:

        raise ValueError(
            "No text could be extracted "
            "from this PDF, even after OCR."
        )

    print(
        "PDF TEXT EXTRACTION: "
        f"OCR successful ({len(ocr_text)} characters)"
    )

    return ocr_text