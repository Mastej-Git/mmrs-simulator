run:
	poetry run python3.13 ./main.py

build:
ruff_check:
	ruff check .

ruff_fix:
	ruff check --fix .

setup-env:
	poetry env use python3.13
	poetry install --no-root
	@echo ""
	@echo "Done. To use the virtualenv run: poetry env activate"
	@echo "Or: source $$(poetry env info --path)/bin/activate"

.PHONY: run ruff_check ruff_fix setup-env