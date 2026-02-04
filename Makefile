.PHONY: help install clean test lint format run venv setup demo

# Default target
help:
	@echo "ClawBot - AI-powered Windows automation"
	@echo ""
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@echo "  help     Show this help message"
	@echo "  venv     Create virtual environment with uv"
	@echo "  install  Install dependencies"
	@echo "  clean    Remove build artifacts and cache"
	@echo "  test     Run tests with pytest"
	@echo "  lint     Run linter (ruff)"
	@echo "  format   Format code (ruff format)"
	@echo "  run      Run the main application"
	@echo "  setup    Run interactive setup wizard"
	@echo "  demo     Run the Calculator demo"
	@echo ""

# Create virtual environment
venv:
	uv venv
	@echo "Virtual environment created. Activate with: source .venv/bin/activate"

# Install dependencies
install:
	uv pip install -e ".[dev]"

# Install with native Windows support
install-native:
	uv pip install -e ".[dev,native]"

# Remove build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf src/*.egg-info/
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	rm -rf .mypy_cache/
	rm -rf __pycache__/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Run tests
test:
	pytest tests/ -v --cov=src/clawbot --cov-report=term-missing

# Run linter
lint:
	ruff check src/ tests/
	ruff format --check src/ tests/

# Format code
format:
	ruff check --fix src/ tests/
	ruff format src/ tests/

# Type checking
typecheck:
	mypy src/clawbot/

# Run the main application
run:
	clawbot --help

# Run setup wizard
setup:
	clawbot setup

# Run demo
demo:
	clawbot demo

# Pull required Ollama model
pull-model:
	ollama pull qwen2.5:3b

# Start VM (Docker Compose)
vm-up:
	docker-compose up -d

# Stop VM
vm-down:
	docker-compose down

# View VM logs
vm-logs:
	docker-compose logs -f
