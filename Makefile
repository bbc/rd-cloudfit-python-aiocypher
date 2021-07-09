USE_VERSION_FILE=TRUE
VERSION:=$(shell python3 setup.py --version)
NEXT_VERSION=$(VERSION)
CUSTOM_GITIGNORE_FILE=TRUE

MS_DOCKER_UNITTEST=FALSE

include commontooling/make/standalone.mk
include commontooling/make/pythonic.mk
include commontooling/make/docker.mk

# Run unit tests with docker-compose and databases
test: ms_docker-build-unittest
	{ \
		$(DOCKER_COMPOSE) run --rm tests; \
		EXIT_CODE=$$?; \
		$(DOCKER_COMPOSE) down; \
		exit $$EXIT_CODE; \
	}

