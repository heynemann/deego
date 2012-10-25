test:
	@PYTHONPATH=${PYTHONPATH}:. pyvows -vv --progress --profile --cover -l deego vows/

ci_test:
	@PYTHONPATH=${PYTHONPATH}:. pyvows --profile --cover -l deego vows/

setup:
	@pip install -r python_requirements

