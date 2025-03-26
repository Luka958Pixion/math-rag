#!/bin/sh
set -e

poetry install --no-root --with dev
poetry run pre-commit install
poetry run python -m ipykernel install --user --name=math_rag --display-name "Python (math_rag)"
