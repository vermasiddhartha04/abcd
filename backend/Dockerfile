FROM python:3.13-slim

WORKDIR /app

# System dependencies required for PDF/OCR processing
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    libglib2.0-0 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first for better Docker caching
COPY backend/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt

# Copy backend application
COPY backend/app /app/app

# Create required directories
RUN mkdir -p /app/app/uploads \
    /app/app/logs \
    /app/data

# Backend port
EXPOSE 8000

# Start FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
