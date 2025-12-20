help:
	@echo Developer commands for cicerone
	@echo
	@grep -E '^[ .a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo

install:  ## Install requirements ready for development
	uv sync

deploy-docs:  ## Build and deploy the documentation
	uv run mkdocs build
	uv run mkdocs gh-deploy


run-docs:  ## Run a local server to view the documentation
	uv run mkdocs serve --watch docs/

release:  ## Build a new version and release it
	uv build
	uv publish

ty: ## Run a static syntax check
	uv run ty check .

format: ## Format the code correctly
	uv run ruff format .
	uv run ruff check --fix .

clean:  ## Clear any cache files and test files
	rm -rf .ty_cache
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf test_output
	rm -rf site/
	rm -rf dist/
	rm -rf **/__pycache__
	rm -rf **/*.pyc
	rm -rf .coverage

test:  ## Run tests
	uv run pytest -vvv

test-cov:  ## Run tests with coverage report
	uv run pytest -vvv --cov=cicerone --cov-report=term-missing --cov-report=html

shell:  ## Run an ipython shell
	uv run ipython
