run:
	python3.10 ./main.py

ruff_check:
	ruff check .

ruff_fix:
	ruff check --fix .

.PHONY: run ruff_check ruff_fix