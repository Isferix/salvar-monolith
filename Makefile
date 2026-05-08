-include .env

PYTHON := uv run python
COMPILE_SCRIPT := .deploy/scripts/compile.py
SECRETS_SCRIPT := .deploy/scripts/gen_secrets.py

API_WORKSPACE := api
WEB_WORKSPACE := web

GITHUB_SSH_KEY := $(GITHUB_SSH_KEY_PATH)
export GITHUB_SSH_KEY

PROJECT_NAME := $(PROJECT_NAME)
export PROJECT_NAME

.PHONY: compile secrets up down rebuild logs ps test-deploy api-up web-up

define run_with_agent
	@ssh-add $(GITHUB_SSH_KEY_PATH) 2>/dev/null || true; \
	$(1)
endef

compile:
	$(PYTHON) $(COMPILE_SCRIPT)

secrets:
	$(PYTHON) $(SECRETS_SCRIPT)

api-up:
	$(call run_with_agent, devcontainer up --workspace-folder $(API_WORKSPACE))

web-up:
	$(call run_with_agent, devcontainer up --workspace-folder $(WEB_WORKSPACE))

up: compile
	$(MAKE) api-up
# 	$(MAKE) web-up

down:
	devcontainer down --workspace-folder $(API_WORKSPACE)
# 	devcontainer down --workspace-folder $(WEB_WORKSPACE)

rebuild: compile
	devcontainer build --workspace-folder $(API_WORKSPACE) --no-cache
	devcontainer build --workspace-folder $(WEB_WORKSPACE) --no-cache
	$(MAKE) up

logs:
	@echo "Usar: docker logs <container>"

ps:
	docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

test-deploy: compile
	$(call run_with_agent, docker compose -p $(PROJECT_NAME)-prod -f .deploy/docker-compose.prod.local.yml build)
	docker compose -p $(PROJECT_NAME)-prod -f .deploy/docker-compose.prod.local.yml up -d