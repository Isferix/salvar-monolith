#!/bin/bash

echo "🔍 Verificando entorno"
make compile
# if [ -z "$(docker compose -f .deploy/docker-compose.dev.yml ps -q)" ]; then
#   echo "Compilando proyecto"
#   make up
# fi

echo "🐳 Preparando devcontainers..."

devcontainer up --workspace-folder api
# devcontainer up --workspace-folder web

echo "🧠 Abriendo VS Code..."

code .
code api/api_zen.code-workspace
# code web/web_zen.code-workspace