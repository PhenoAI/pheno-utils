#!/bin/bash

# Static code analysis for Python project
echo "Starting Static Code Analysis..."

# Bandit: discovers potential security issues
echo "Running Bandit..."
bandit -r .

# Black: checks Python code formatting
echo "Running Black..."
black --check .

# Flake8: checks for style guide enforcement
echo "Running Flake8..."
flake8 .

# iSort: checks Python import formatting
echo "Running iSort..."
isort . --check-only

# Mypy: checks for type annotation
echo "Running Mypy..."
mypy --config-file mypy.ini --install-types --non-interactive .

# Pycodestyle: checks Python code against PEP 8 style guide
echo "Running Pycodestyle..."
pycodestyle .

# Pylint: checks Python code for errors, tries to enforce a coding standard
echo "Running Pylint..."
pylint **/*.py

# Radon: checks Python code complexity
echo "Running Radon CC..."
radon cc **/*.py

echo "Running Radon MI..."
radon mi **/*.py

echo "Static Code Analysis Complete"
