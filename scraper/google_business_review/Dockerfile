FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN useradd -m -u 10001 appuser

WORKDIR /app

FROM base AS builder

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

COPY pyproject.toml /app/
COPY core/src /app/core/src
COPY google_business_review/src /app/google_business_review/src

RUN uv pip install --system .

FROM base AS runtime

COPY --from=builder /usr/local /usr/local
COPY --from=builder /app /app

USER appuser

EXPOSE 8000

CMD ["uvicorn", "google_business_review.main:app", "--host", "0.0.0.0", "--port", "8000"]
