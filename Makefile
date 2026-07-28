.DEFAULT_GOAL := help
.PHONY: coverage deps format help lint test typecheck

coverage:  ## Run tests with coverage
	uv run coverage erase
	uv run coverage run -m pytest -ra
	uv run coverage report -m

deps:  ## Install dependencies
	uv sync

lint:  ## Linting of source code
	uv run black --check sruthi examples tests
	uv run ruff check sruthi examples tests

typecheck:  ## Static type checking of source code
	uv run mypy

format:  ## Format source code (black codestyle) and apply lint fixes
	uv run black sruthi examples tests
	uv run ruff check --fix sruthi examples tests

test:  ## Run tests
	uv run pytest --cov=sruthi tests/

help: SHELL := /bin/bash
help: ## Show help message
	@IFS=$$'\n' ; \
	help_lines=(`fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##/:/'`); \
	printf "%s\n\n" "Usage: make [task]"; \
	printf "%-20s %s\n" "task" "help" ; \
	printf "%-20s %s\n" "------" "----" ; \
	for help_line in $${help_lines[@]}; do \
		IFS=$$':' ; \
		help_split=($$help_line) ; \
		help_command=`echo $${help_split[0]} | sed -e 's/^ *//' -e 's/ *$$//'` ; \
		help_info=`echo $${help_split[2]} | sed -e 's/^ *//' -e 's/ *$$//'` ; \
		printf '\033[36m'; \
		printf "%-20s %s" $$help_command ; \
		printf '\033[0m'; \
		printf "%s\n" $$help_info; \
	done
