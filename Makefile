.PHONY: install \
		migrate \
		clean \
		run \
		test \
		coverage \
		
.DEFAULT_GOAL := run

PROJECT_NAME = mussels
VENV_DIR ?= .env
BIN_DIR = $(VENV_DIR)/bin
PYTHON = $(BIN_DIR)/python
PIP = $(PYTHON)
MANAGE = $(PYTHON) manage.py
SETTINGS_MODULE = $(DJANGO_SETTINGS_MODULE)
ifeq ($(strip $(SETTINGS_MODULE)),)
SETTINGS_MODULE = $(PROJECT_NAME).settings
endif

install:
	$(PIP) install -r requirements.txt

migrate:
	$(MANAGE) syncdb
	$(MANAGE) migrate

clean:
	find . -iname "*.pyc" -delete
	find . -iname "*.pyo" -delete
	find . -iname "__pycache__" -delete

host ?= 0.0.0.0
port ?= 8000
run:
	$(MANAGE) runserver $(host):$(port)

test:
	$(MANAGE) test $(test)

# go to '0.0.0.0:8000/htmlcov/index.html' to view coverage
coverage:
	coverage run ./manage.py test $(test) && coverage html

