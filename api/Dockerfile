ARG PYTHON_VERSION=3.13.13-alpine

# ---------- BASE ----------
FROM python:${PYTHON_VERSION} AS base

ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

WORKDIR /code

FROM base AS build
ENV UV_PROJECT_ENVIRONMENT=/opt/venv 

RUN apk add --no-cache git openssh-client
# Install uv binary only for build stages
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN mkdir -p -m 0700 ~/.ssh && \
    ssh-keyscan github.com >> ~/.ssh/known_hosts
COPY pyproject.toml uv.lock ./
RUN --mount=type=ssh uv sync --no-dev --frozen --no-cache
COPY . .

# ---------- DEVELOPMENT ----------
FROM build AS dev
RUN apk add --no-cache nano curl sqlite bash

RUN adduser -D -s /bin/sh vscode
RUN chown -R vscode:vscode /opt/venv /code
USER vscode

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "src.main:server", "--host", "0.0.0.0", "--reload", "--proxy-headers", "--forwarded-allow-ips", "*"]
# CMD ["sleep", "infinity"]

# ---------- RUNTIME (PROD) ----------
FROM base AS runtime

RUN adduser -D -u 10001 -s /bin/sh appuser
# Copy only the virtualenv and source code
COPY --chown=appuser:appuser --from=build /opt/venv /opt/venv
COPY --chown=appuser:appuser --from=build /code/src ./src

USER appuser
EXPOSE 8000
CMD ["uvicorn", "src.main:server", "--active", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips","*"]