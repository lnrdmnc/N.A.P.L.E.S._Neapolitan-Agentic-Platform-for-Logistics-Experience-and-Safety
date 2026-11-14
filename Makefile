.PHONY: check

check:
	@for f in CLAUDE.md README.md docs/STATO.md .env.example; do \
		test -f "$$f" || { echo "check: manca $$f"; exit 1; }; \
	done
	@if git ls-files --error-unmatch .env >/dev/null 2>&1; then \
		echo "check: .env e' tracciato da git"; exit 1; \
	fi
	@echo "check: ok"
