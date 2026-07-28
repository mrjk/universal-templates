.PHONY: help lint test

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  %-12s %s\n", $$1, $$2}'

lint: ## Run shellcheck on *.sh (if available)
	@command -v shellcheck >/dev/null 2>&1 || { echo "shellcheck not installed"; exit 1; }
	@find . -name '*.sh' -not -path './.git/*' -print0 | xargs -0 -r shellcheck

test: ## Run project tests (override in your Makefile)
	@echo "No tests configured — override the test target"
