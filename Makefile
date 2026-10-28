PROJECT_NAME = ElementsOfDataScience
PYTHON_INTERPRETER = python

## mamba solves this environment much faster than conda; use conda if that is
## what you have
CONDA = mamba

.PHONY: default notebooks publish site publish-site tests tests-soln format tests-book

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

## Build and publish. The build targets only change the working tree; the
## publish targets push to GitHub, which is what readers see.
notebooks:
	./build.sh

publish:
	@test -n "$(MSG)" || (echo 'usage: make publish MSG="commit message"'; exit 1)
	./publish.sh "$(MSG)"

site:
	jb/build.sh

publish-site:
	jb/publish.sh

## The student notebooks (solutions removed), and jupyter_intro
tests:
	pytest --nbmake [01]*.ipynb jupyter_intro.ipynb

## The notebooks with solutions. soln/utils.py is a symlink, which Windows
## checks out as a text file, so CI runs this only on Linux and macOS.
tests-soln:
	cd soln && pytest --nbmake [01]*.ipynb

## Format the code in soln/ (ruff.toml), then list lines still over the
## limit (strings and comments, which the formatter doesn't wrap).
format:
	ruff format
	ruff check --select E501 --output-format concise || true

## Smoke tests for the LeanPub files in book/leanpub/ (run book/emit.py
## --release first). Set EPUBCHECK=/path/to/epubcheck.jar to validate the EPUBs.
tests-book:
	cd book && pytest test_book.py
