.PHONY: clean clean-test clean-pyc clean-build doc help
.DEFAULT_GOAL := help
SHELL=/bin/bash


include dev.mk
include help.mk

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -rf {} +
	find . -name '*.egg' -exec rm -rf {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -rf {} +
	find . -name '*.pyo' -exec rm -rf {} +
	find . -name '*~' -exec rm -rf {} +
	find . -name '__pycache__' -exec rm -rf {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

lint: ## check style with pylint
	source venv/bin/activate && \
	pre-commit run --all-files && \
	black --check dep_check && \
	black --check tests && \
	black --check tests_go && \
	isort --check-only -rc dep_check && \
	isort --check-only -rc tests && \
	isort --check-only -rc tests_go && \
	mypy dep_check && \
	pylint dep_check tests tests_go

test: ## run tests quickly with the default Python
	source venv/bin/activate && \
	pytest -v tests

test-go: ## run tests regarding go
	source venv/bin/activate && \
	pytest -v tests_go

test-all: ## run tests on every Python version with tox
	source venv/bin/activate && \
	tox

coverage: ## check code coverage quickly with the default Python
	coverage run --source dep_check -m pytest
	coverage report -m
	coverage html
	xdg-open htmlcov/index.html

install: clean ## install the package to the active Python's site-packages
	python3.7 setup.py install

dist: clean ## builds source and wheel package
	source venv/bin/activate && \
	python3.7 setup.py sdist && \
	python3.7 setup.py bdist_wheel
