clean:
	rm -rf build dist *.egg-info temp


build: clean
	python -m build --sdist --wheel


manual-test-upload:
	python -m twine upload --repository testpypi dist/* --config-file pypi-test-auth


tests:
	. venv/bin/activate
	pytest test/*