FROM node:22-alpine

WORKDIR /workspace

RUN corepack enable && corepack prepare pnpm@latest --activate
RUN pnpm add eslint eslint-plugin-jinja eslint-plugin-html prettier
 
USER node