FROM python:3.13-slim

# System deps
RUN apt-get update && apt-get install -y \
    git curl build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv binary only for build stages
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Usuario no root
RUN useradd -ms /bin/bash vscode

RUN mkdir -p /opt/venv && chown -R vscode:vscode /opt/venv 
RUN mkdir -p /home/vscode/.cache/uv && chown -R vscode:vscode /home/vscode/.cache/uv

RUN echo "vscode ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

USER vscode
WORKDIR /workspaces

# Opcional: entorno virtual manejado por uv
ENV VIRTUAL_ENV=/opt/venv
ENV UV_PROJECT_ENVIRONMENT=/opt/venv 
ENV PATH="/opt/venv/bin:$PATH"
ENV UV_LINK_MODE=copy
ENV UV_CACHE_DIR=/home/vscode/.cache/uv