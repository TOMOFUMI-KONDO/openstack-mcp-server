.PHONY: help deps run test

# Variables
MAIN_FILE := main.py

# Default target
help:
	@echo "Available targets:"
	@echo "  deps         - Install dependencies"
	@echo "  run          - Run the server with --help"
	@echo "  test         - Run tests"

# Install dependencies
deps:
	pip install -r requirements.txt

# Run the application
run:
	python3 $(MAIN_FILE) --help

# Run tests
test:
	pytest -v
