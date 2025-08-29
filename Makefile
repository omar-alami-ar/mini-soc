# Wazuh SOC Testing Suite Makefile

.PHONY: help install test test-ui test-api test-integration test-quick test-all health clean

# Default target
help:
	@echo "🔒 Wazuh SOC Testing Suite"
	@echo "=========================="
	@echo ""
	@echo "Available targets:"
	@echo "  install        - Install Python dependencies"
	@echo "  test           - Run all tests"
	@echo "  test-ui        - Run UI tests only"
	@echo "  test-api       - Run API tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  test-quick     - Run quick tests (skip optional/slow)"
	@echo "  test-all       - Run all tests with full output"
	@echo "  health         - Run health check only"
	@echo "  clean          - Clean test results and cache"
	@echo "  setup          - Setup testing environment"
	@echo "  lint           - Run code linting"
	@echo "  format         - Format code with black"
	@echo ""

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	pip install -r requirements-test.txt

# Setup testing environment
setup: install
	@echo "🔧 Setting up testing environment..."
	mkdir -p test-results
	@if [ ! -f .env ]; then \
		echo "⚠️  No .env file found. Please copy env.example to .env and configure your settings."; \
		cp env.example .env; \
		echo "✅ Created .env from env.example"; \
		echo "📝 Please edit .env with your actual Wazuh deployment details"; \
	fi

# Run all tests
test: setup
	@echo "🧪 Running all tests..."
	python run_tests.py --all

# Run UI tests only
test-ui: setup
	@echo "🖥️  Running UI tests..."
	python run_tests.py --ui

# Run API tests only
test-api: setup
	@echo "🔌 Running API tests..."
	python run_tests.py --api

# Run integration tests only
test-integration: setup
	@echo "🔗 Running integration tests..."
	python run_tests.py --integration

# Run quick tests (skip optional and slow)
test-quick: setup
	@echo "⚡ Running quick tests..."
	python run_tests.py --quick

# Run all tests with full output
test-all: setup
	@echo "🧪 Running all tests with full output..."
	python -m pytest tests/ -v -s --tb=long

# Run health check only
health: setup
	@echo "💓 Running health check..."
	python run_tests.py --health

# Quick health check (standalone script)
health-check:
	@echo "💓 Running standalone health check..."
	python health_check.py

# Clean test results and cache
clean:
	@echo "🧹 Cleaning up..."
	rm -rf test-results/
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	rm -rf tests/__pycache__/
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	@echo "✅ Cleanup complete"

# Run code linting
lint: setup
	@echo "🔍 Running code linting..."
	@if command -v flake8 >/dev/null 2>&1; then \
		flake8 tests/ --max-line-length=100 --ignore=E501,W503; \
	else \
		echo "⚠️  flake8 not found. Install with: pip install flake8"; \
	fi

# Format code with black
format: setup
	@echo "🎨 Formatting code..."
	@if command -v black >/dev/null 2>&1; then \
		black tests/ --line-length=100; \
	else \
		echo "⚠️  black not found. Install with: pip install black"; \
	fi

# Development workflow
dev: format lint test-quick

# CI/CD workflow
ci: install test-quick

# Production deployment check
prod-check: install health test-quick

# Show test coverage
coverage: setup
	@echo "📊 Running tests with coverage..."
	@if command -v coverage >/dev/null 2>&1; then \
		coverage run -m pytest tests/; \
		coverage report; \
		coverage html; \
		echo "📁 Coverage report generated in htmlcov/"; \
	else \
		echo "⚠️  coverage not found. Install with: pip install coverage"; \
	fi

# Run specific test file
test-file:
	@if [ -z "$(FILE)" ]; then \
		echo "❌ Please specify FILE=<filename>"; \
		echo "Example: make test-file FILE=test_dashboard_ui.py"; \
		exit 1; \
	fi
	@echo "🧪 Running tests from $(FILE)..."
	python -m pytest tests/$(FILE) -v

# Run specific test class
test-class:
	@if [ -z "$(CLASS)" ]; then \
		echo "❌ Please specify CLASS=<ClassName>"; \
		echo "Example: make test-class CLASS=TestWazuhDashboardUI"; \
		exit 1; \
	fi
	@echo "🧪 Running tests from class $(CLASS)..."
	python -m pytest tests/ -k "$(CLASS)" -v

# Run specific test method
test-method:
	@if [ -z "$(METHOD)" ]; then \
		echo "❌ Please specify METHOD=<method_name>"; \
		echo "Example: make test-method METHOD=test_dashboard_https_accessible"; \
		exit 1; \
	fi
	@echo "🧪 Running test method $(METHOD)..."
	python -m pytest tests/ -k "$(METHOD)" -v

# Show help for test-file, test-class, and test-method
test-help:
	@echo "🔍 Specific Test Targets:"
	@echo "  test-file FILE=<filename>     - Run tests from specific file"
	@echo "  test-class CLASS=<ClassName>  - Run tests from specific class"
	@echo "  test-method METHOD=<method>   - Run specific test method"
	@echo ""
	@echo "Examples:"
	@echo "  make test-file FILE=test_dashboard_ui.py"
	@echo "  make test-class CLASS=TestWazuhDashboardUI"
	@echo "  make test-method METHOD=test_dashboard_https_accessible" 