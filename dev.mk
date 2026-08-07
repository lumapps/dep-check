PYTHON?=.venv/bin/python3
UV?=$(PYTHON) -m uv

# Initialize the development environment, e.g. the Python dependencies
init: .venv
	$(UV) sync
	pre-commit install

# Make sure the virtualenv exists
.venv:
	$(PYTHON_EXEC) -m venv .venv
	pip install --quiet --upgrade pip uv

update_requirements:
	UV_EXCLUDE_NEWER="1 week" $(UV) lock --upgrade
