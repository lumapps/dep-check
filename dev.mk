# Initialize the development environment, e.g. the Python dependencies
init: venv dev-requirements.txt
	source venv/bin/activate && \
	pip-sync \
		--quiet \
		dev-requirements.txt
	source venv/bin/activate && \
	pre-commit install

# Make sure the virtualenv exists
venv:
	$(PYTHON_EXEC) -m venv venv
	source venv/bin/activate && \
	pip install --quiet --upgrade pip
	source venv/bin/activate && \
	pip install --quiet pip-tools

update_requirements:
	# Remove the virtualenv and the requirements lock files
	rm -rf venv requirements.txt dev-requirements.txt
	# Recrete the virtualenv
	$(MAKE) venv
	# Generate the lock file for production requirements
	source venv/bin/activate && \
	pip-compile \
		--quiet \
		--generate-hashes \
		--output-file requirements.txt
	# Generate the lock file for development requirements
	source venv/bin/activate && \
	pip-compile \
		--quiet \
		--generate-hashes \
		--output-file dev-requirements.txt \
		setup.py \
		dev-requirements.in
	# Install all the requirements in the virtualenv
	$(MAKE) init
