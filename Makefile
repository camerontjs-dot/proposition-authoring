.PHONY: bootstrap test

bootstrap:
	python scripts/fetch_frozen_predecessors.py

test:
	python -m unittest discover -s tests -v
