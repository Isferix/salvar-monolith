#!/bin/bash

# echo "🔍 Verificando entorno"
# make compile

echo "🐳 Preparando devcontainers..."
make up

# devcontainer up --workspace-folder api
# devcontainer up --workspace-folder web

echo "🧠 Abriendo VS Code..."

code .
code core/zen.code-workspace
code api/zen.code-workspace
code web/zen.code-workspace