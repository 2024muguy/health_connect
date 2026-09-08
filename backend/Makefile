# ============================================
# HealthConnect AI - Makefile
# ============================================
.PHONY: help build up down logs test test-unit test-integration notebook shell migrate migrate-up migrate-down seed clean

# Default target
.DEFAULT_GOAL := help

# Variables
DOCKER_COMPOSE = docker-compose
APP_CONTAINER = healthconnect-app
WORKER_CONTAINER = healthconnect-worker
NOTEBOOK_CONTAINER = healthconnect-notebook

help: ## Show help message
	@echo "HealthConnect AI - Available Commands"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Build all Docker images
	$(DOCKER_COMPOSE) build

build-no-cache: ## Build images without cache
	$(DOCKER_COMPOSE) build --no-cache

up: ## Start all services in background
	$(DOCKER_COMPOSE) up -d

up-app: ## Start only app service
	$(DOCKER_COMPOSE) up -d app

up-worker: ## Start only worker service
	$(DOCKER_COMPOSE) up -d worker

up-notebook: ## Start only notebook service
	$(DOCKER_COMPOSE) up -d notebook

down: ## Stop all services
	$(DOCKER_COMPOSE) down

down-volumes: ## Stop services and remove volumes
	$(DOCKER_COMPOSE) down -v

restart: ## Restart all services
	$(DOCKER_COMPOSE) restart

logs: ## View logs for all services
	$(DOCKER_COMPOSE) logs -f

logs-app: ## View app logs
	$(DOCKER_COMPOSE) logs -f app

logs-worker: ## View worker logs
	$(DOCKER_COMPOSE) logs -f worker

logs-notebook: ## View notebook logs
	$(DOCKER_COMPOSE) logs -f notebook

ps: ## Show running containers
	$(DOCKER_COMPOSE) ps

shell: ## Enter app container shell
	docker exec -it $(APP_CONTAINER) bash

shell-worker: ## Enter worker container shell
	docker exec -it $(WORKER_CONTAINER) bash

shell-notebook: ## Enter notebook container shell
	docker exec -it $(NOTEBOOK_CONTAINER) bash

test: ## Run all tests
	docker exec -it $(APP_CONTAINER) pytest tests/ -v

test-unit: ## Run unit tests
	docker exec -it $(APP_CONTAINER) pytest tests/ -v -m "unit"

test-integration: ## Run integration tests
	docker exec -it $(APP_CONTAINER) pytest tests/ -v -m "integration"

test-api: ## Run API tests
	docker exec -it $(APP_CONTAINER) pytest tests/test_api/ -v

test-rag: ## Run RAG tests
	docker exec -it $(APP_CONTAINER) pytest tests/test_rag/ -v

test-agents: ## Run agent tests
	docker exec -it $(APP_CONTAINER) pytest tests/test_agents/ -v

test-cov: ## Run tests with coverage
	docker exec -it $(APP_CONTAINER) pytest tests/ --cov=app --cov-report=html

migrate-init: ## Initialize migrations
	docker exec -it $(APP_CONTAINER) alembic init migrations

migrate-create: ## Create new migration
	docker exec -it $(APP_CONTAINER) alembic revision --autogenerate -m "auto migration"

migrate-up: ## Apply migrations
	docker exec -it $(APP_CONTAINER) alembic upgrade head

migrate-down: ## Rollback migration
	docker exec -it $(APP_CONTAINER) alembic downgrade -1

seed: ## Seed database with sample data
	docker exec -it $(APP_CONTAINER) python scripts/seed_data.py

ingest: ## Ingest knowledge base into vector store
	docker exec -it $(APP_CONTAINER) python scripts/ingest_knowledge_base.py

train-intent: ## Train intent classifier
	docker exec -it $(NOTEBOOK_CONTAINER) python scripts/train_intent_classifier.py

train-safety: ## Train safety classifier
	docker exec -it $(NOTEBOOK_CONTAINER) python scripts/train_safety_classifier.py

evaluate: ## Evaluate models
	docker exec -it $(NOTEBOOK_CONTAINER) python scripts/evaluate_models.py

format: ## Format code with black
	docker exec -it $(APP_CONTAINER) black app/ tests/

lint: ## Lint code with flake8
	docker exec -it $(APP_CONTAINER) flake8 app/ tests/

type-check: ## Type check with mypy
	docker exec -it $(APP_CONTAINER) mypy app/

clean: ## Remove all containers, volumes, and images
	$(DOCKER_COMPOSE) down -v --rmi all

clean-cache: ## Clean Python cache files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name "*.pyd" -delete 2>/dev/null || true