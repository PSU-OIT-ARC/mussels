.PHONY: install \
		migrate \
		clean \
		run \
		test \
		coverage \

.DEFAULT_GOAL := run

export PATH:=.env/bin:$(PATH):/usr/pgsql-9.3/bin:/usr/pgsql-9.1/bin
PYTHON=python3
MANAGE = $(PYTHON) manage.py

install: .env
	createdb mussels
	psql -c "CREATE EXTENSION postgis" mussels
	python generateimages.py
	$(MANAGE) migrate
	$(MANAGE) loaddata species.json substrates.json
	$(MANAGE) loaddata dummy.json
	echo "Use your ODIN username for your username!"
	$(MANAGE) createsuperuser

clean:
	find . -iname "*.pyc" -delete
	find . -iname "*.pyo" -delete
	find . -iname "__pycache__" -delete

host ?= 0.0.0.0
port ?= 8000
run: .env
	$(MANAGE) runserver $(host):$(port)

.env:
	$(PYTHON) -m venv .env
	curl https://raw.githubusercontent.com/pypa/pip/master/contrib/get-pip.py | python
	pip install -r requirements.txt
