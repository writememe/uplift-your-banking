.DEFAULT_GOAL := help

.PHONY: help
help:
	@grep '^[a-zA-Z]' $(MAKEFILE_LIST) | \
	sort | \
	awk -F ':.*?## ' 'NF==2 {printf "\033[35m  %-25s\033[0m %s\n", $$1, $$2}'

.PHONY:	lint-all
lint-all:	ruff-format-check ruff-check yamllint bandit mypy ## Perform all linting and security checks (ruff, yamllint, bandit and mypy).


.PHONY:	ruff-format-check
ruff-format-check: ## Format check code using ruff
	@echo "--- Performing ruff reformatting checks ---"
	poetry run ruff format --check .

.PHONY:	ruff-format
ruff-format: ## Format code using ruff
	@echo "--- Performing ruff reformatting ---"
	poetry run ruff format

.PHONY:	ruff-check
ruff-check: ## Check code using ruff
	@echo "--- Performing ruff checks ---"
	poetry run ruff check

.PHONY:	yamllint
yamllint:	## Perform YAML linting using yamllint
	@echo "--- Performing yamllint linting ---"
	poetry run yamllint .

.PHONY: bandit
bandit:	## Perform python code security checks using bandit
	@echo "--- Performing bandit code security scanning ---"
	poetry run bandit . --configfile pyproject.toml --recursive --format json --verbose

.PHONY: mypy
mypy:	## Perform mypy type hint checking using mypy
	@echo "--- Performing mypy type hint checking ---"
	poetry run mypy . --config-file pyproject.toml
