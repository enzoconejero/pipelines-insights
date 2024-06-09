clean:
	rm -rf build dist *.egg-info


build:
	python -m build --sdist --wheel


manual-test-upload:
	python -m twine upload --repository testpypi dist/* --config-file pypi-test-auth
