from pypdf import PdfReader


def extract_text_from_pdf(
    file_path: str,
) -> str:
    reader = PdfReader(file_path)

    text_parts = []

    for page_number, page in enumerate(
        reader.pages,
        start=1,
    ):
        page_text = page.extract_text()

        if page_text:
            text_parts.append(
                f"\n--- Page {page_number} ---\n"
            )
            text_parts.append(page_text)

    return "\n".join(text_parts).strip()