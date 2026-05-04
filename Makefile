-include .env

PYTHON := uv run python
COMPILE_SCRIPT := .deploy/scripts/compile.py
SECRETS_SCRIPT := .deploy/scripts/gen_secrets.py
COMPOSE_FILE := .deploy/docker-compose.dev.yml

GITHUB_SSH_KEY := $(GITHUB_SSH_KEY_PATH)
export GITHUB_SSH_KEY

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
	$(call run_with_agent, docker compose -f $(COMPOSE_FILE) up -d --build)

down:
	docker compose -f $(COMPOSE_FILE) down

logs:
	docker compose -f $(COMPOSE_FILE) logs -f

ps:
	docker compose -f $(COMPOSE_FILE) ps

rebuild: compile render-env
	docker compose -f $(COMPOSE_FILE) up -d --build --force-recreate

test-deploy: compile render-env
	$(call run_with_agent, docker compose -f .deploy/docker-compose.prod.local.yml build)
	docker compose -f .deploy/docker-compose.prod.local.yml up -d