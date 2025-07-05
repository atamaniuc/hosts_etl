# 🧪 Host Data ETL Pipeline - Makefile
# 
# This Makefile provides commands to build, run, test, and maintain the ETL pipeline
# that processes host data from Qualys and Crowdstrike APIs with hybrid pagination.

# Declare all targets as phony (not real files)
.PHONY: help build up down start stop install run test coverage lint format type-check check-all-linters logs shell

# 📖 Help Command

## Show help for all available commands
help:
	@echo "🧪 Host Data ETL Pipeline - Available Commands"
	@echo ""
	@echo "🏗️  BUILD AND INFRASTRUCTURE:"
	@echo "  build          - Build the Docker image"
	@echo "  up             - Start all services in background (MongoDB + App)"
	@echo "  down           - Stop and remove all containers"
	@echo "  start          - Start existing containers"
	@echo "  stop           - Stop running containers"
	@echo ""
	@echo "🚀  PIPELINE EXECUTION:"
	@echo "  install        - Complete setup: request API token, create .env, build, start, and run pipeline"
	@echo "  run            - Run the complete ETL pipeline with hybrid pagination"
	@echo ""
	@echo "🧪  TESTING AND QUALITY ASSURANCE:"
	@echo "  test           - Run all unit tests with verbose output"
	@echo "  coverage       - Run tests with coverage report"
	@echo ""
	@echo "🔍  CODE QUALITY AND LINTING:"
	@echo "  lint           - Run pylint for code quality checks"
	@echo "  format         - Format code using Black formatter"
	@echo "  type-check     - Run mypy for type checking"
	@echo "  check-all-linters - Run all code quality checks: format, lint, and type-check"
	@echo ""
	@echo "📊  MONITORING AND DEBUGGING:"
	@echo "  logs           - View real-time application and db logs"
	@echo "  shell          - Open interactive shell in the app container"
	@echo ""
	@echo "💡  TIP: Use 'make help' to show this help message"

# 🏗️ Build and Infrastructure Commands

## Build the Docker image
build:
	docker compose build

## Start all services in background (MongoDB + App)
up:
	docker compose up -d --remove-orphans

## Stop and remove all containers
down:
	docker compose down

## Start existing containers
start:
	docker compose start

## Stop running containers
stop:
	docker compose stop

# 🚀 Pipeline Execution Commands

## Run the complete ETL pipeline with hybrid pagination
## Fetches data from Qualys and Crowdstrike APIs, normalizes, deduplicates, and stores in MongoDB
run:
	docker compose exec app python main.py

## Complete setup: build, start services, and run pipeline
install:
	@echo "🔧 Setting up ETL Pipeline..."
	@echo "📝 Creating .env file..."
	@while [ -z "$$token" ]; do \
		echo "Please enter your API token:"; \
		read -p "API Token: " token; \
		if [ -z "$$token" ]; then \
			echo "❌ Token cannot be empty. Please try again."; \
		fi; \
	done; \
	echo "API_TOKEN=$$token" > ./app/.env; \
	echo "MONGO_URI=mongodb://mongo:27017" >> ./app/.env; \
	echo "✅ .env file created successfully!"
	@echo "🏗️ Building Docker image..."
	@docker compose build
	@echo "🚀 Starting services..."
	@docker compose up -d --remove-orphans
	@echo "⏳ Waiting for services to be ready..."
	@sleep 5
	@echo "▶️ Running ETL pipeline..."
	@docker compose exec app python main.py

# 🧪 Testing and Quality Assurance Commands

## Run all unit tests with verbose output
test:
	docker compose exec app pytest -sv

## Run tests with coverage report
coverage:
	docker compose exec app pytest --cov=app --cov-report=term-missing

# 🔍 Code Quality and Linting Commands

## Run pylint for code quality checks
lint:
	docker compose exec app pylint .

## Format code using Black formatter
format:
	docker compose exec app black .

## Run mypy for type checking
type-check:
	docker compose exec app mypy .

## Run all code quality checks: format, lint, and type-check
check-all-linters: format lint type-check

# 📊 Monitoring and Debugging Commands

## View real-time application and db logs
logs:
	docker compose logs -f

## Open interactive shell in the app container
shell:
	docker compose exec app /bin/bash
