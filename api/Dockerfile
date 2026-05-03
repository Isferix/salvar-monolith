ARG PYTHON_VERSION=3.13.7-alpine

# ---------- BASE ----------
FROM python:${PYTHON_VERSION} AS base

WORKDIR /code

# Install uv binary only for build stages
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# ---------- DEPENDENCIES ----------
FROM base AS deps

COPY pyproject.toml uv.lock ./

# Create venv and install dependencies and init db
RUN uv sync --frozen --no-cache

# ---------- BUILD ----------
FROM base AS build

COPY --from=deps /code/.venv /code/.venv
COPY . .

# ---------- DEVELOPMENT ----------
FROM build AS dev

ENV PATH="/code/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "src.main:server", "--host", "0.0.0.0", "--reload", "--proxy-headers", "--forwarded-allow-ips","*"]

# ---------- RUNTIME (PROD) ----------
FROM python:${PYTHON_VERSION} AS runtime

WORKDIR /code

# Copy only the virtualenv and source code
COPY --from=deps /code/.venv ./.venv
COPY --from=build /code/src ./src

ENV PATH="/code/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "src.main:server", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips","*"]