.PHONY: help install-backend install-frontend test compile frontend-build verify compose-up compose-down

help:
	@echo "install-backend  Install Python dependencies"
	@echo "install-frontend Install frontend dependencies"
	@echo "test             Run backend tests"
	@echo "compile          Compile Python sources"
	@echo "frontend-build   Build React UI"
	@echo "verify           Run repository static verifier"
	@echo "compose-up       Start local stack"

install-backend:
	python -m pip install -r backend/requirements.txt pytest

install-frontend:
	cd frontend && npm install --no-audit --no-fund

test:
	cd backend && PYTHONPATH=. python -m pytest -q

compile:
	cd backend && python -m compileall -q .

frontend-build:
	cd frontend && npm run build

verify:
	python scripts/verify_repository.py

compose-up:
	docker compose up --build

compose-down:
	docker compose down
