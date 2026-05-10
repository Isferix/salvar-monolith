install:
	uv sync --group dev

lint:
	uv run ruff check .

test:
	uv run pytest -v

build:
	uv build .

ci: install lint test

test-build: lint test build