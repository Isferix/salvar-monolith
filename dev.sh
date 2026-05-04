#!/bin/bash

echo "🔍 Verificando entorno"
if [ ! -f "./.deploy/.env" ]; then
  echo "Compilando proyecto"
  make up
fi

echo "🐳 Preparando devcontainers..."

devcontainer up --workspace-folder api
# devcontainer up --workspace-folder web

echo "🧠 Abriendo VS Code..."

code .
code api/api_zen.code-workspace
# code web/web_zen.code-workspace