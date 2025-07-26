.PHONY: help deps run test

# Variables
MAIN_FILE := main.py

# Default target
help:
	@echo "Available targets:"
	@echo "  deps         - Install dependencies"
	@echo "  fmt          - Format the code"
	@echo "  run          - Run the server with --help"
	@echo "  test         - Run tests"

# Install dependencies
deps:
	pip install -r requirements.txt

# Format the code
fmt:
	black . --config ~/pyproject.toml
	isort . --profile black --settings-path ~/pyproject.toml

# Run the application
run:
	python3 $(MAIN_FILE) --help

# Run tests
test:
	pytest -v --cov --cov-branch
