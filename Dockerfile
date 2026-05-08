ARG PYTHON_VERSION=3.13-slim

# ---------- BASE ----------
FROM python:${PYTHON_VERSION} AS base

ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

WORKDIR /code

# ---------- BUILD ----------
FROM base AS build

ENV UV_PROJECT_ENVIRONMENT=/opt/venv 

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*

    # Install uv binary only for build stages
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN mkdir -p -m 0700 ~/.ssh && \
    ssh-keyscan github.com >> ~/.ssh/known_hosts

    COPY ./api/pyproject.toml ./api/uv.lock ./
RUN --mount=type=ssh uv sync --no-dev --frozen --no-cache

# ---------- DEVELOPMENT ----------
FROM build AS dev
RUN useradd -m -s /bin/sh vscode

ENV UV_LINK_MODE=copy
ENV UV_CACHE_DIR=/home/vscode/.cache/uv

COPY --chown=vscode:vscode ./api ./

RUN mkdir -p /home/vscode/.cache/uv 
RUN chown -R vscode:vscode /opt/venv /code /home/vscode/.cache/uv
USER vscode

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "src.main:server", "--host", "0.0.0.0", "--reload", "--proxy-headers", "--forwarded-allow-ips", "*"]
# CMD ["sleep", "infinity"]

# ---------- RUNTIME (PROD) ----------
FROM base AS runtime

RUN useradd -m -u 10001 -U -s /bin/sh appuser
# Copy only the virtualenv and source code
COPY --chown=appuser:appuser --from=build /opt/venv /opt/venv
COPY --chown=appuser:appuser --from=build /code/src ./src
COPY --chown=appuser:appuser ./web /code/web

USER appuser
EXPOSE 8000
CMD ["uvicorn", "src.main:server", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips","*"]
# CMD ["sleep", "infinity"]
