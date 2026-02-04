.PHONY: help install clean test lint format run venv setup demo check build release shell status screenshot config

# Default target
help:
	@echo "DeskPilot - AI-powered desktop automation"
	@echo ""
	@echo "Usage: make <target>"
	@echo ""
	@echo "Development:"
	@echo "  venv           Create virtual environment with uv"
	@echo "  install        Install dependencies"
	@echo "  install-native Install with native Windows support"
	@echo "  clean          Remove build artifacts and cache"
	@echo ""
	@echo "Quality:"
	@echo "  test           Run tests with pytest"
	@echo "  lint           Run linter (ruff)"
	@echo "  format         Format code (ruff format)"
	@echo "  typecheck      Run type checking (mypy)"
	@echo "  check          Run all quality checks"
	@echo ""
	@echo "Running:"
	@echo "  run            Show help"
	@echo "  setup          Run interactive setup wizard"
	@echo "  demo           Run the Calculator demo"
	@echo "  status         Check system status"
	@echo "  config         Show current configuration"
	@echo "  screenshot     Take a screenshot"
	@echo "  shell          Open Python shell with deskpilot"
	@echo ""
	@echo "VM Management:"
	@echo "  vm-up          Start Windows VM (Docker)"
	@echo "  vm-down        Stop Windows VM"
	@echo "  vm-logs        View VM logs"
	@echo "  pull-model     Download Ollama model"
	@echo ""
	@echo "Packaging:"
	@echo "  build          Build package"
	@echo "  release        Build release tarball"
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
	pytest tests/ -v --cov=src/deskpilot --cov-report=term-missing

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
	mypy src/deskpilot/

# Run the main application
run:
	deskpilot --help

# Run setup wizard
setup:
	deskpilot setup

# Run demo
demo:
	deskpilot demo

# Show configuration
config:
	deskpilot config

# Check system status
status:
	deskpilot status

# Take a screenshot
screenshot:
	deskpilot screenshot --save

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

# Start VM (Docker Compose)
vm-up:
	docker-compose up -d

# Stop VM
vm-down:
	docker-compose down

# View VM logs
vm-logs:
	docker-compose logs -f
