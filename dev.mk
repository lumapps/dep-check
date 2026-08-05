PYTHON?=venv/bin/python3
UV?=$(PYTHON) -m uv
export UV_PROJECT_ENVIRONMENT=venv

# Initialize the development environment, e.g. the Python dependencies
init: venv
	$(UV) sync --locked
	pre-commit install

# Make sure the virtualenv exists
venv:
	$(PYTHON_EXEC) -m venv venv
	pip install --quiet --upgrade pip uv

update_requirements:
	# Remove the virtualenv and the lock file
	rm -rf venv uv.lock
	# Recrete the virtualenv
	$(MAKE) venv
	# Generate the lock file for the project and its dependency groups
	$(UV) lock
	# Install all the requirements in the virtualenv
	$(MAKE) init
