test:
	@sudo PYTHONPATH=${PYTHONPATH}:~/.virtualenvs/deego/lib/python2.7/site-packages/:/usr/lib/python2.7/dist-packages/:. ~/.virtualenvs/deego/bin/pyvows -vv --progress --profile --cover -l deego vows/

ci_test:
	@PYTHONPATH=${PYTHONPATH}:. pyvows --profile --cover -l deego vows/

setup:
	@pip install -r python_requirements

