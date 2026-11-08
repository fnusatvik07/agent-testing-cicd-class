# The same commands CI runs. If `make ci` passes on your laptop, the pipeline should pass too.

lint:
	ruff check .

test:
	pytest tests -v

evals:
	deepeval test run evals/
	python evals/report.py

ci: lint test evals

.PHONY: lint test evals ci
