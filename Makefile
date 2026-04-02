.PHONY: install dev test test-unit test-integration lint format run docker-build docker-up

install:
	pip install -e .

dev:
	pip install -e ".[dev]"

test:
	pytest tests/ -v --cov=enterprise_skills_lib --cov-report=term-missing

test-unit:
	pytest tests/unit/ -v --cov=enterprise_skills_lib

test-integration:
	pytest tests/integration/ -v -m integration

lint:
	ruff check enterprise_skills_lib/ skills/ api/ tests/

format:
	ruff format enterprise_skills_lib/ skills/ api/ tests/

run:
	uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

docker-build:
	docker build -t copaw-enterprise-skills .

docker-up:
	docker compose up -d
