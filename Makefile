.PHONY: install test lint run dev clean docker-build docker-run

install:
	pip install -e ".[dev]"

install-cli:
	cd cli && npm install && npm run build

test:
	python -m pytest tests/ -v --tb=short

test-cov:
	python -m pytest tests/ -v --cov=orca --cov-report=term-missing

lint:
	ruff check orca/ tests/ --fix

format:
	ruff format orca/ tests/

run:
	uvicorn orca.gateway.app:app --host 0.0.0.0 --port 8000 --reload

dev:
	uvicorn orca.gateway.app:app --host 0.0.0.0 --port 8000 --reload --log-level debug

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
	find . -type f -name "*.pyc" -delete 2>/dev/null

docker-build:
	docker build -t orca:latest .

docker-run:
	docker run -p 8000:8000 --env-file .env orca:latest

skills-sync:
	@echo "Syncing skills from source projects..."
	@cp -r ../feynman-main/skills/* skills/public/ 2>/dev/null || true
	@cp -r ../deer-flow-main/skills/public/* skills/public/ 2>/dev/null || true
	@echo "Skills synced: $$(ls skills/public/ | wc -l) skills"

help:
	@echo "Orca Commands:"
	@echo "  make install       Install Python package"
	@echo "  make install-cli   Build TypeScript CLI"
	@echo "  make test          Run tests"
	@echo "  make test-cov      Run tests with coverage"
	@echo "  make lint          Lint code"
	@echo "  make run           Start Gateway server"
	@echo "  make dev           Start in dev mode"
	@echo "  make docker-build  Build Docker image"
	@echo "  make docker-run    Run Docker container"
	@echo "  make skills-sync   Sync skills from source projects"
