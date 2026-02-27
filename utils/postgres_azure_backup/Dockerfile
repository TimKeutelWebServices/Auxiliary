# Multi-stage build for PostgreSQL backup service
FROM python:3.11-slim AS base

# Install PostgreSQL client tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Stage 1: Builder
FROM base AS builder

# Copy project files
COPY pyproject.toml ./
COPY src ./src

# Install dependencies
RUN pip install --no-cache-dir --user -e .

# Stage 2: Runtime
FROM base AS runtime

# Create non-root user for security
RUN useradd -m -u 1001 backupuser

# Copy installed packages from builder
COPY --from=builder /root/.local /home/backupuser/.local

# Copy application code
COPY --from=builder /app/src /app/src
COPY --chown=backupuser:backupuser .env.example /app/.env.example

WORKDIR /app

# Set Python path
ENV PATH=/home/backupuser/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

USER backupuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Run the backup service
CMD ["python", "-m", "postgres_azure_backup.backup_service"]
