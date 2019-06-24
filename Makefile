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

lint: ## check style with flake8
	flake8 dep-check tests

test: ## run tests quickly with the default Python
	py.test

test-all: ## run tests on every Python version with tox
	tox

coverage: ## check code coverage quickly with the default Python
	coverage run --source dep-check -m pytest
	coverage report -m
	coverage html
	xdg-open htmlcov/index.html

doc: ## generate Sphinx HTML documentation, including API doc
	rm -f doc/dep-check.rst
	rm -f doc/modules.rst
	sphinx-apidoc -o doc/ dep-check
	$(MAKE) -C doc clean
	$(MAKE) -C doc html
	xdg-open doc/_build/html/index.html

servedoc: doc ## compile the doc watching for changes
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C doc html' -R -D .

release: dist ## package and upload a release
	twine upload dist/*

dist: clean ## builds source and wheel package
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

install: clean ## install the package to the active Python's site-packages
	python setup.py install
