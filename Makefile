# Claude Code Notifier - Development Commands

.PHONY: help install test format lint typecheck check clean

help: ## Show this help
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

# ============================================================================
# CORE DEVELOPMENT
# ============================================================================

install: ## Install development dependencies
	pip install -e ".[dev]"

format: ## Format code with ruff
	@ruff format src/ tests/ && echo "✅ FORMAT: PASSED" || (echo "❌ FORMAT: FAILED" && false)

lint: ## Lint with ruff
	@ruff check src/ tests/ --output-format=github && echo "✅ LINT: PASSED" || (echo "❌ LINT: FAILED" && false)

typecheck: ## Type check with mypy
	@mypy && echo "✅ TYPECHECK: PASSED" || (echo "❌ TYPECHECK: FAILED" && false)

test: ## Run tests
	@pytest && echo "✅ TEST: PASSED" || (echo "❌ TEST: FAILED" && false)

check: ## Run comprehensive quality checks
	@echo "🔍 Running comprehensive quality checks..."
	@$(MAKE) -k format lint typecheck test && echo "\n🎉 CHECK PASSED" || echo "\n❌ CHECK FAILED"

fix: ## Auto-fix all issues (format + lint + cleanup)
	@echo "🔧 Auto-fixing all issues..."
	@ruff format src/ tests/ && echo "✅ FORMAT-FIX: APPLIED" || echo "⚠️ FORMAT-FIX: ISSUES FOUND"
	@ruff check src/ tests/ --fix --unsafe-fixes && echo "✅ LINT-FIX: APPLIED" || echo "⚠️ LINT-FIX: SOME ISSUES REMAIN"
	@echo "🎉 Auto-fixes completed (run 'make check' to see remaining issues)"

clean: ## Clean up temporary files
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -delete
	find . -type d -name ".ruff_cache" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	@echo "✅ Cleaned temporary files"
