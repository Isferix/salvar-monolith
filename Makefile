-include .env

PYTHON := uv run python
COMPILE_SCRIPT := .deploy/scripts/compile.py
SECRETS_SCRIPT := .deploy/scripts/gen_secrets.py
COMPOSE_FILE := .deploy/docker-compose.dev.yml

GITHUB_SSH_KEY := $(GITHUB_SSH_KEY_PATH)
export GITHUB_SSH_KEY

PROJECT_NAME := $(PROJECT_NAME)
export PROJECT_NAME

COMPOSE_PROJECT_NAME := $(PROJECT_NAME)-compose
export COMPOSE_PROJECT_NAME

.PHONY: up down logs ps rebuild test-deploy

# define run_with_agent
# 	@export $$(cat .env | xargs) && \
# 	eval "$$(ssh-agent -s)" && \
# 	ssh-add $(GITHUB_SSH_KEY_PATH) && \
# 	$(1) && \
# 	eval "$$(ssh-agent -k)"
# endef
define run_with_agent
	@ssh-add $(GITHUB_SSH_KEY_PATH) 2>/dev/null || true; \
	$(1)
endef

compile:
	$(PYTHON) $(COMPILE_SCRIPT)

secrets:
	$(PYTHON) $(SECRETS_SCRIPT)
	
up: compile
	$(call run_with_agent, docker compose -p $(COMPOSE_PROJECT_NAME) -f $(COMPOSE_FILE) up -d --build)

down:
	docker compose -p $(COMPOSE_PROJECT_NAME) -f $(COMPOSE_FILE) down

logs:
	docker compose -p $(COMPOSE_PROJECT_NAME) -f $(COMPOSE_FILE) logs -f

ps:
	docker compose -p $(COMPOSE_PROJECT_NAME) -f $(COMPOSE_FILE) ps

rebuild: compile render-env
	docker compose -p $(COMPOSE_PROJECT_NAME) -f $(COMPOSE_FILE) up -d --build --force-recreate

test-deploy: compile render-env
	$(call run_with_agent, docker compose -p $(PROJECT_NAME)-prod -f .deploy/docker-compose.prod.local.yml build)
	docker compose -p $(PROJECT_NAME)-prod -f .deploy/docker-compose.prod.local.yml up -d