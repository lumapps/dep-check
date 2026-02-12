PYTHON?=venv/bin/python3
PIP_COMPILE?=$(PYTHON) -m uv pip compile --quiet --generate-hashes --strip-extras --python-platform=linux
PIP_SYNC?=$(PYTHON) -m uv pip sync

# Initialize the development environment, e.g. the Python dependencies
init: venv dev-requirements.txt
	$(PIP_SYNC) \
		dev-requirements.txt
	pre-commit install

# Make sure the virtualenv exists
venv:
	$(PYTHON_EXEC) -m venv venv
	pip install --quiet --upgrade pip uv

update_requirements:
	# Remove the virtualenv and the requirements lock files
	rm -rf venv requirements.txt dev-requirements.txt
	# Recrete the virtualenv
	$(MAKE) venv
	# Generate the lock file for production requirements
	$(PIP_COMPILE) \
		--output-file requirements.txt \
		pyproject.toml
	# Generate the lock file for development requirements
	$(PIP_COMPILE) \
		--output-file dev-requirements.txt \
		pyproject.toml \
		dev-requirements.in
	# Install all the requirements in the virtualenv
	$(MAKE) init
