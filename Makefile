.SILENT: help
.PHONY: help fmt lint test dev shell docs

uv-run = uv run

UID := $(shell id -u)
GID := $(shell id -g)

remote.url := $(shell git config --get remote.origin.url)
ifeq ($(remote.url),)
    # If no remote URL, get the top-level directory of the Git repository
    project.dir := $(shell git rev-parse --show-toplevel)
    # Extract the project name from the directory name
    project.name := $(notdir $(project.dir))
else
    # If remote URL exists, extract the project name from the remote URL
    project.name := $(shell basename $(remote.url) .git)
endif

DEV_TAG = $(project.name)-dev

help:
	echo "Available targets:"
	cat $(MAKEFILE_LIST) | \
	grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' | \
	awk 'BEGIN { FS = ":.*?## " } \
	{ cnt++; a[cnt] = $$1; b[cnt] = $$2; if (length($$1) > max) max = length($$1) } \
	END { for (i = 1; i <= cnt; i++) \
		printf "  $(shell tput setaf 6)%-*s$(shell tput setaf 0) %s\n", max, a[i], b[i] }'
	tput sgr0

fmt: ## Format code
	@echo "Formatting code..."
	$(uv-run) ruff check --fix
	$(uv-run) ruff format
	@echo "Formatting Completed!"

lint: ## Lint code
	@echo "Linting code..."
	if [ "${CI}" = "true" ]; then \
		$(uv-run) ruff check --output-format=github; \
	else \
		$(uv-run) ruff check; \
	fi
	$(uv-run) ruff format --check
	$(uv-run) mypy .
	@echo "Linting Completed!"

test: ## Run tests
	$(uv-run) pytest

dev: ## Build dev container
	docker build --build-arg UID=$(UID) --build-arg GID=$(GID) --tag $(DEV_TAG) --target dev .

shell: dev ## Enter dev container
	docker run --rm -it -v .:/app -w /app $(DEV_TAG) bash

docs: ## Build docs
	$(uv-run) --only-group doc mkdocs build
