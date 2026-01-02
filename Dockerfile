# --- 1. BASE ---
FROM python:3.11-slim AS base
WORKDIR /app
ENV PATH="/opt/venv/bin:$PATH"

# --- 2. BUILDER ---
FROM base AS builder
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- 3. DEVELOPMENT ---
FROM base AS development
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv
COPY ./scripts/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]


