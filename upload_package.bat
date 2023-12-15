@echo off

REM Remove dist and build directories
rmdir /s /q dist
rmdir /s /q build
del /q goodgit_windows.egg-info

REM Build the package
python setup.py sdist bdist_wheel

REM Upload the package using twine
twine upload --repository pypi dist/* -u __token__ -p api-token