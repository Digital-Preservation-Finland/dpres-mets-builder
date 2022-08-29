DESTDIR ?= /
PREFIX ?= /usr
PYTHON ?= python3

install:
	# Cleanup temporary files
	rm -f INSTALLED_FILES

	# Use Python setuptools
	${PYTHON} ./setup.py install -O1 --prefix="${PREFIX}" --root="${DESTDIR}" --record=INSTALLED_FILES

test:
	python3 -m pytest -svvv tests/

coverage:
	python3 -m pytest -svvv --cov=mets_builder --cov-fail-under=80 --cov-report=term-missing tests
