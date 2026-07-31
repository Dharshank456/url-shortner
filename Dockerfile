FROM python:3.12-slim

# -----------------------------
# Python Runtime Settings
# -----------------------------
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000

# -----------------------------
# Create application directory
# -----------------------------
WORKDIR /app

# -----------------------------
# Install OS dependencies
# -----------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------
# Create non-root user
# -----------------------------
RUN groupadd -r appuser && \
    useradd -r -g appuser appuser

# -----------------------------
# Install Python dependencies
# -----------------------------
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# -----------------------------
# Copy application
# -----------------------------
COPY . .

# -----------------------------
# Set ownership
# -----------------------------
RUN chown -R appuser:appuser /app

USER appuser

# -----------------------------
# Expose Port
# -----------------------------
EXPOSE 5000

# -----------------------------
# Health Check
# -----------------------------
HEALTHCHECK --interval=30s \
            --timeout=5s \
            --start-period=20s \
            --retries=3 \
CMD curl -f http://localhost:5000/health || exit 1

# -----------------------------
# Start Gunicorn
# -----------------------------
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "4", "--timeout", "120", "app:app"]
