SHELL=/bin/bash
BASE_DIR:=.
ORDER_API_BASE_DIR:=$(BASE_DIR)/order-api/
USER_API_BASE_DIR:=$(BASE_DIR)/user-api/

BASE_DOCKER_COMPOSE_ORDER_FILE:=$(ORDER_API_BASE_DIR)/docker-compose.yml
BASE_DOCKER_COMPOSE_USER_FILE:=$(USER_API_BASE_DIR)/docker-compose.yml

DOCKER_COMPOSE_ORDER:=docker-compose -f $(BASE_DOCKER_COMPOSE_ORDER_FILE)
DOCKER_COMPOSE_USER:=docker-compose -f $(BASE_DOCKER_COMPOSE_USER_FILE)


help:
	@echo 'Usage:'
	@echo '  make order-api              Build and run order-api project separately                             '
	@echo '  make user-api               Build and run user-api project separately                              '
	@echo '  make run           		 Build and run the project, including order-api and user-api            '
	@echo ''

order:
	cd order-api;
	if [ -f $(BASE_DOCKER_COMPOSE_ORDER_FILE) ]; then $(DOCKER_COMPOSE_ORDER) build; fi;
	if [ -f $(BASE_DOCKER_COMPOSE_ORDER_FILE) ]; then $(DOCKER_COMPOSE_ORDER) up -d; fi	

user:
	cd user-api;
	if [ -f $(BASE_DOCKER_COMPOSE_USER_FILE) ]; then $(DOCKER_COMPOSE_USER) build; fi;
	if [ -f $(BASE_DOCKER_COMPOSE_USER_FILE) ]; then $(DOCKER_COMPOSE_USER) up -d; fi

run:
	make user;
	make order;