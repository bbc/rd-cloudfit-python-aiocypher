MS_DOCKER_UNITTEST:=FALSE

# Import of psycopg2, which is used in aiopg and aiocypher unit tests, failed on Python 3.13.
# psycopg2 reports support up to 3.12. See also https://github.com/psycopg/psycopg2/issues/1692
CLOUDFIT_BASE_LABEL:=3.12

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
