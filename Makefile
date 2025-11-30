.EXPORT_ALL_VARIABLES:

# if you wrap everything in uv run, it runs slower.
ifeq ($(origin VIRTUAL_ENV),undefined)
    VENV := uv run
else
    VENV :=
endif

uv.lock: pyproject.toml
	@echo "Installing dependencies"
	@uv sync --all-extras

clean-pyc:
	@echo "Removing compiled files"



# tests can't be expected to pass if dependencies aren't installed.
# tests are often slow and linting is fast, so run tests on linted code.
test: uv.lock
	@echo "Running unit tests"
	# $(VENV) pytest --doctest-modules fermi_problems
	# $(VENV) python -m unittest discover
	$(VENV) pytest tests -vv -n 2 --cov=fermi_problems --cov-report=html --cov-fail-under 20 --cov-branch --cov-report=xml --junitxml=junit.xml -o junit_family=legacy --timeout=5 --session-timeout=600
	#$(VENV) bash ./scripts/basic_checks.sh
#	$(VENV) bash basic_test_with_logging.sh


isort: 
	@echo "Formatting imports"
	$(VENV) isort .


black: isort 
	@echo "Formatting code"
	$(VENV) metametameta pep621
	$(VENV) black fermi_problems # --exclude .venv
	$(VENV) black tests # --exclude .venv


pre-commit:  isort black
	@echo "Pre-commit checks"
	$(VENV) pre-commit run --all-files

bandit:  
	@echo "Security checks"
	# $(VENV)  bandit fermi_problems -r --quiet



pylint:isort black 
	@echo "Linting with pylint"
	$(VENV) ruff check --fix fermi_problems
	$(VENV) pylint fermi_problems --fail-under 9.4


check: mypy test pylint bandit pre-commit

publish: testf
	rm -rf dist && $(VENV) hatch build

mypy:
	$(VENV) echo $$PYTHONPATH
	$(VENV) mypy fermi_problems --ignore-missing-imports --check-untyped-defs


check_docs:
	$(VENV) interrogate fermi_problems --verbose  --fail-under 70
	$(VENV) pydoctest --config .pydoctest.json | grep -v "__init__" | grep -v "__main__" | grep -v "Unable to parse"

make_docs:
	pdoc fermi_problems --html -o docs --force

check_md:
	$(VENV) linkcheckMarkdown README.md
	$(VENV) markdownlint README.md --config .markdownlintrc
	$(VENV) mdformat README.md docs/*.md


check_spelling:
	$(VENV) pylint fermi_problems --enable C0402 --rcfile=.pylintrc_spell
	$(VENV) pylint docs --enable C0402 --rcfile=.pylintrc_spell
	$(VENV) codespell README.md --ignore-words=private_dictionary.txt
	$(VENV) codespell fermi_problems --ignore-words=private_dictionary.txt
	$(VENV) codespell docs --ignore-words=private_dictionary.txt

check_changelog:
	# pipx install keepachangelog-manager
	$(VENV) changelogmanager validate

check_all_docs: check_docs check_md check_spelling check_changelog

check_self:
	# Can it verify itself?
	$(VENV) ./scripts/dog_food.sh
