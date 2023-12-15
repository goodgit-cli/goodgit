@echo off

REM Remove dist and build directories
rmdir /s /q dist
rmdir /s /q build
del /q goodgit_windows.egg-info

REM Build the package
python setup.py sdist bdist_wheel

REM Upload the package using twine
twine upload --repository pypi dist/* -u __token__ -p pypi-AgEIcHlwaS5vcmcCJGVlNmFmMWQ5LTJiZGItNDJjNy05OWIxLTM0ZmQ1ZTk4NWY4MwACD1sxLFsiZ29vZGdpdCJdXQACLFsyLFsiN2M3YjI2ODItOTIxOS00ZWY4LWFmN2UtY2MyMGYwOTk2NDA0Il1dAAAGIIaFkNA5rk76iZ-eMDsNOV20Zzd_dkoqXO5JHarr9aep