test:
	python3 -m pytest -svvv tests/

coverage:
	python3 -m pytest -svvv --cov=mets_builder --cov-fail-under=80 --cov-report=term-missing tests
