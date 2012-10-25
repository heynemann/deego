test:
	@PYTHONPATH=${PYTHONPATH}:. pyvows --progress --profile --cover -l deego vows/

setup:
	@pip install -r python_requirements

