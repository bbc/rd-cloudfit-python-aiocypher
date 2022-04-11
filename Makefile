USE_VERSION_FILE:=TRUE
MS_DOCKER_UNITTEST:=FALSE

include ./static-commontooling/make/lib_static_commontooling.mk
include ./static-commontooling/make/standalone.mk
include ./static-commontooling/make/pythonic.mk
include ./static-commontooling/make/docker.mk

# Unit tests here are a bit special and use docker-compose
test: ms_docker-build-unittest
	{ \
		$(DOCKER_COMPOSE) run --rm tests; \
		EXIT_CODE=$$?; \
		$(DOCKER_COMPOSE) down; \
		exit $$EXIT_CODE; \
	}
