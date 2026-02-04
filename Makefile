.PHONY: help install clean test lint format run venv demo check build release shell status screenshot config docker-build docker-run docker-push

# Default target
help:
	@echo "DeskPilot - AI-powered desktop automation"
	@echo ""
	@echo "Usage: make <target>"
	@echo ""
	@echo "Development:"
	@echo "  venv           Create virtual environment with uv"
	@echo "  install        Install dependencies (includes native packages)"
	@echo "  clean          Remove build artifacts and cache"
	@echo ""
	@echo "Quality:"
	@echo "  test           Run tests with pytest"
	@echo "  test-e2e       Run e2e tests (requires Docker demo running)"
	@echo "  lint           Run linter (ruff)"
	@echo "  format         Format code (ruff format)"
	@echo "  typecheck      Run type checking (mypy)"
	@echo "  check          Run all quality checks"
	@echo ""
	@echo "Running:"
	@echo "  run            Show help"
	@echo "  demo           Run the Calculator demo"
	@echo "  status         Check system status"
	@echo "  config         Show current configuration"
	@echo "  screenshot     Take a screenshot"
	@echo "  shell          Open Python shell with deskpilot"
	@echo ""
	@echo "Docker (Demo Environment):"
	@echo "  docker-build   Build the demo Docker image"
	@echo "  docker-run     Run the demo container"
	@echo "  docker-stop    Stop the demo container"
	@echo "  docker-push    Push demo image to registry"
	@echo ""
	@echo "Packaging:"
	@echo "  build          Build package"
	@echo "  release        Build release tarball"
	@echo ""

# Create virtual environment
venv:
	uv venv
	@echo "Virtual environment created. Activate with: source .venv/bin/activate"

# Install dependencies (native packages included by default)
install:
	uv pip install -e ".[dev]"

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
	.venv/bin/pytest tests/ -v --cov=src/deskpilot --cov-report=term-missing --ignore=tests/e2e

# Run e2e tests (requires Docker demo running)
test-e2e:
	@echo "Make sure docker demo is running: make docker-run"
	DESKPILOT_E2E=1 .venv/bin/pytest tests/e2e/ -v --tb=short

# Run linter
lint:
	.venv/bin/ruff check src/ tests/
	.venv/bin/ruff format --check src/ tests/

# Format code
format:
	.venv/bin/ruff check --fix src/ tests/
	.venv/bin/ruff format src/ tests/

# Type checking
typecheck:
	.venv/bin/mypy src/deskpilot/

# Run the main application
run:
	.venv/bin/deskpilot --help

# Run demo
demo:
	.venv/bin/deskpilot demo

# Show configuration
config:
	.venv/bin/deskpilot config

# Check system status
status:
	.venv/bin/deskpilot status

# Take a screenshot
screenshot:
	.venv/bin/deskpilot screenshot --save

# Open Python shell with deskpilot
shell:
	.venv/bin/python -c "from deskpilot.wizard.config import get_config; print('Config loaded:', get_config()); import code; code.interact(local=locals())"

# Run all quality checks
check: lint typecheck test
	@echo "All checks passed!"

# Build package
build:
	uv build

# Build release tarball
release: clean build
	@echo "Release built in dist/"

# Pull required Ollama model
pull-model:
	ollama pull qwen2.5:3b

# Docker demo targets
docker-build:
	docker build -f docker/Dockerfile.demo -t deskpilot/demo:latest .

docker-run:
	docker-compose up -d
	@echo ""
	@echo "Demo container starting..."
	@echo "Open http://localhost:8006 in your browser"
	@echo ""

docker-stop:
	docker-compose down

docker-push:
	docker push deskpilot/demo:latest
