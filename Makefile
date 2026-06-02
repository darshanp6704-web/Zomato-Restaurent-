.PHONY: run-cli run-web run-backend run-frontend setup-frontend test lint clean help

VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
PYTEST = $(VENV)/bin/pytest
STREAMLIT = $(VENV)/bin/streamlit

help:
	@echo "AI-Powered Restaurant Recommendation System - Developer Workflow"
	@echo "Available commands:"
	@echo "  make run-cli       - Run the CLI application interactively"
	@echo "  make run-web       - Run the Streamlit web application (legacy UI)"
	@echo "  make run-backend   - Run the FastAPI REST API backend on port 8000"
	@echo "  make setup-frontend- Install React/Vite frontend packages"
	@echo "  make run-frontend  - Run the React/Vite development server on port 3000"
	@echo "  make test          - Run all pytest unit and integration tests"
	@echo "  make lint          - Check code syntax using black and flake8"
	@echo "  make clean         - Clean python caches and the Parquet dataset cache"

run-cli:
	$(PYTHON) app/main.py -i

run-web:
	$(STREAMLIT) run app/streamlit_app.py

run-backend:
	$(PYTHON) -m uvicorn app.api:app --host 127.0.0.1 --port 8000 --reload

setup-frontend:
	cd frontend && npm install

run-frontend:
	cd frontend && npm run dev

test:
	$(PYTEST) tests/ -v

lint:
	$(PYTHON) -m pip install flake8 black --quiet
	$(PYTHON) -m flake8 app/ domain/ llm/ presentation/ data/ tests/
	$(PYTHON) -m black --check app/ domain/ llm/ presentation/ data/ tests/

clean:
	rm -rf .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -f data/cache/restaurants.parquet
