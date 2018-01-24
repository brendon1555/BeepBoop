@ECHO OFF

if "%1" == "dist" (
    python setup.py clean
	python setup.py sdist
)

:end