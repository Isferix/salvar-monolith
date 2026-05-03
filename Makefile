COMPILE_SCRIPT := .deploy/scripts/compile.py
SECRETS_SCRIPT := .deploy/scripts/gen_secrets.py
COMPOSE_FILE := .deploy/docker-compose.dev.yml

.PHONY: up down logs ps rebuild test-deploy

compile:
	python3 $(COMPILE_SCRIPT)

secrets:
	python3 $(SECRETS_SCRIPT)
	
up: compile
	docker compose -f $(COMPOSE_FILE) up -d --build

down:
	docker compose -f $(COMPOSE_FILE) down

logs:
	docker compose -f $(COMPOSE_FILE) logs -f

ps:
	docker compose -f $(COMPOSE_FILE) ps

rebuild: compile
	docker compose -f $(COMPOSE_FILE) up -d --build --force-recreate

test-deploy: compile
	docker compose -f .deploy/docker-compose.prod.local.yml build
	docker compose -f .deploy/docker-compose.prod.local.yml up -d