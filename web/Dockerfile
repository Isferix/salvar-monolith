# ---------- BASE ----------
FROM node:20-alpine AS base
WORKDIR /app

# ---------- BUILD ----------
FROM base AS build
ENV COREPACK_ENABLE_DOWNLOAD_PROMPT=0
# Instalamos pnpm globalmente
RUN corepack enable && corepack prepare pnpm@latest --activate
COPY package.json pnpm-lock.yaml* ./
RUN pnpm install --frozen-lockfile

# ---------- DEVELOPMENT ----------
FROM build AS dev
# Instalamos solo prod para la imagen base (opcional si vas a sobreescribir en dev)
RUN apk add --no-cache shadow

# usuario tipo devcontainer
RUN adduser -D vscode

COPY --chown=vscode:vscode . .

RUN chown -R vscode:vscode /app
USER vscode

EXPOSE 5173
CMD ["pnpm", "dev", "--host"]
# CMD ["sleep", "infinity"]

# ---------- RUNTIME (STATIC) ----------
# FROM nginx:alpine AS runtime
# COPY --from=build /app/dist /usr/share/nginx/html
# EXPOSE 80