# Initialize the development environment, e.g. the Python dependencies
init: venv requirements.txt dev-requirements.txt
	source venv/bin/activate && \
	pip-sync \
		--quiet \
		requirements.txt dev-requirements.txt

# Make sure the virtualenv exists
venv:
	${SYSTEM_PYTHON_EXEC} -m venv venv
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
		setup.cfg \
		dev-requirements.in
	# Install all the requirements in the virtualenv
	$(MAKE) init
