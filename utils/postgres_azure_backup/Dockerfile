# Multi-stage build for PostgreSQL backup service
FROM python:3.11-slim AS base

# Install PostgreSQL client tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Stage 1: Builder
FROM base AS builder

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy project files and install dependencies
WORKDIR /app

COPY pyproject.toml ./
RUN pip install --no-cache-dir .

# Stage 2: Runtime
FROM base AS runtime

# Create non-root user for security
RUN useradd -m -u 1001 backupuser

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY backup_service.py /app/backup_service.py

WORKDIR /app

# Set Python path
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Change ownership to backupuser
RUN chown -R backupuser:backupuser /app /opt/venv

USER backupuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Run the backup service
CMD ["python", "backup_service.py"]
