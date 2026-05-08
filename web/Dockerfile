FROM node:22-alpine

RUN corepack enable && corepack prepare pnpm@latest --activate
RUN pnpm add eslint prettier
 
WORKDIR /workspace
RUN adduser -D vscode
RUN mkdir -p /workspace && chown -R vscode:vscode /workspace
RUN echo "vscode ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

USER vscode