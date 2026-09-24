PROJECT_NAME = ElementsOfDataScience
PYTHON_INTERPRETER = python

## mamba solves this environment much faster than conda; use conda if that is
## what you have
CONDA = mamba

.PHONY: default

default:
	@echo "No command specified. Please specify a target."

create_environment:
	$(CONDA) env create -f environment.yml
	@echo ">>> conda env created. Activate with:\nconda activate $(PROJECT_NAME)"

update_environment:
	$(CONDA) env update -f environment.yml --prune

delete_environment:
	conda env remove --name $(PROJECT_NAME)

requirements:
	$(PYTHON_INTERPRETER) -m pip install -U pip setuptools wheel
	$(PYTHON_INTERPRETER) -m pip install -r requirements.txt

clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

tests:
	pytest --nbmake [01]*.ipynb
