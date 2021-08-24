SHELL=/bin/bash
BASE_DIR:=..
PROJECT_BASE_DIR:=$(BASE_DIR)/user_api/
PROJECT_NAME:=user-api

BASE_DOCKER_COMPOSE_FILE:=$(BASE_DIR)/docker-compose.yaml
DOCKER_COMPOSE:=docker-compose -p $(PROJECT_NAME) -f $(BASE_DOCKER_COMPOSE_FILE)

help:
	@echo 'Usage:'
	@echo '  make clean                  Remove python compiled files                                           '
	@echo '  make lint                   Run pylama linter                                                      '
	@echo '  make black           		 Install black and run                                                  '
	@echo '  make doc-sphinx             Build and compile project docs with sphinx                             '
	@echo '  make run           		 Run run user-api application                                           '
	@echo ''

clean:
	@find . -iname *.pyc -delete;
	@find . -iname *.pyo -delete;
	@find . -iname __pycache__ -delete;
	@rm -fr build dist .venv-dist;
	@rm -fr .cache .pytest_cache;
	@rm -fr .tox .eggs;
	@find . -iname .coverage -delete;
	@find . -iname *.egg-info -exec rm -fr {} +
	@rm -fr htmlcov coverage.xml;

lint:
	pip install -U pylama;
	pylama -o $(BASE_DIR)/pylama.ini;

black:
	pip install -U black;
	for d in $(PROJECT_BASE_DIR)*/ ; do cd $$d; python -m  black .; cd ..; done;

sort:
	@isort

test: clean black lint
	@black --check esp
	@isort -c
	python -m pytest --cov  --cov-report=xml:coverage.xml --junitxml=junit.xml

doc-sphinx:
	cd ..; cd docs; make clean; make html

run:
	gunicorn --workers=1 --worker-class=uvicorn.workers.UvicornWorker --timeout=174000 --reload --bind=0.0.0.0:7000 'app:start_application()'

build:
	if [ -f $(BASE_DOCKER_COMPOSE_FILE) ]; then $(DOCKER_COMPOSE) build; fi
	for d in $(PROJECT_BASE_DIR)*/ ; do cd $$d; make build; cd ../..; done;

docker-start:
	if [ -f $(BASE_DOCKER_COMPOSE_FILE) ]; then $(DOCKER_COMPOSE) up -d $(CONTAINERS); sleep 10; fi

docker-stop:
	if [ -f $(BASE_DOCKER_COMPOSE_FILE) ]; then $(DOCKER_COMPOSE) down; fi
