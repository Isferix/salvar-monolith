FROM node:22-alpine

WORKDIR /workspace

RUN corepack enable && corepack prepare pnpm@latest --activate
RUN pnpm add eslint prettier @html-eslint/eslint-plugin eslint-plugin-jinja
 
USER node