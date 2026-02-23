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
COPY google_business_opening_hours/src /app/google_business_opening_hours/src

RUN uv pip install --system .

FROM base AS runtime

COPY --from=builder /usr/local /usr/local
COPY --from=builder /app /app

USER appuser

CMD ["python", "-m", "google_business_opening_hours.main"]
