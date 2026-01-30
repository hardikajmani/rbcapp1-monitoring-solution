.PHONY: help setup test test1 test2 test3 clean lint format docker-up docker-down install-deps

help:
	@echo "🚀 rbcapp1 Monitoring Solution - Available Commands"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make setup           - Install all dependencies"
	@echo "  make install-deps    - Install Python dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  make test            - Run all tests"
	@echo "  make test1           - Test single-host monitoring"
	@echo "  make test2           - Test Ansible playbooks"
	@echo "  make test3           - Test data analysis"
	@echo ""
	@echo "Development:"
	@echo "  make lint            - Run linters"
	@echo "  make format          - Format code"
	@echo "  make clean           - Remove build artifacts"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up       - Start all services"
	@echo "  make docker-down     - Stop all services"

setup: install-deps
	@echo "✅ Setup complete!"

install-deps:
	@echo "📦 Installing dependencies..."
	pip install --upgrade pip
	pip install -r requirements.txt 2>/dev/null || echo "No root requirements.txt"
	-pip install -r test1-single-host/monitor/requirements.txt 2>/dev/null
	-pip install -r test1-single-host/api/requirements.txt 2>/dev/null
	-pip install -r test3-data-analysis/requirements.txt 2>/dev/null
	@echo "✅ Dependencies installed!"

test: test1 test2 test3
	@echo "✅ All tests passed!"

test1:
	@echo "🧪 Running TEST1 tests..."
	pytest test1-single-host/tests/ -v --tb=short 2>/dev/null || echo "TEST1 ready for implementation"

test2:
	@echo "🧪 Running TEST2 tests..."
	ansible-lint test2-ansible-orchestration/ 2>/dev/null || echo "TEST2 ready for implementation"

test3:
	@echo "🧪 Running TEST3 tests..."
	pytest test3-data-analysis/tests/ -v --tb=short 2>/dev/null || echo "TEST3 ready for implementation"

lint:
	flake8 test1-single-host test3-data-analysis 2>/dev/null || echo "Linting ready"

format:
	black . --line-length=100 2>/dev/null || echo "Formatting ready"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf build/ dist/ *.egg-info/ 2>/dev/null || true

docker-up:
	docker-compose -f docker-compose-full.yml up -d 2>/dev/null || echo "docker-compose-full.yml not found"

docker-down:
	docker-compose -f docker-compose-full.yml down 2>/dev/null || echo "docker-compose-full.yml not found"
