import os
import uuid

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".doc",
    ".docx",
}

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB


def allowed_file(filename: str):
    extension = os.path.splitext(filename)[1].lower()
    return extension in ALLOWED_EXTENSIONS


def generate_filename(filename: str):
    extension = os.path.splitext(filename)[1].lower()
    return f"{uuid.uuid4().hex}{extension}"