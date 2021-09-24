PYTHON3:=$(shell which python3)
VERSION:=$(shell ${PYTHON3} setup.py --version)
MODNAME:=$(shell ${PYTHON3} setup.py --name)
DOCKER:=$(shell which docker)
DOCKER_COMPOSE:=$(shell which docker-compose)

ifeq "${DOCKER}" ""
$(error docker is required to use this project)
endif

ifeq "${DOCKER_COMPOSE}" ""
$(error docker-compose is required to use this project)
endif

PYTHON_VERSION?=3.6
BUILD_TAG?=local
COMPOSE_PROJECT_NAME?=$(BUILD_TAG)_$(MODNAME)
DOCKER_COMPOSE_EXTRA_ENV?=
DOCKER_COMPOSE_ENV=MODNAME=$(MODNAME) BUILD_TAG=$(BUILD_TAG) $(DOCKER_COMPOSE_EXTRA_ENV)

DOCKER_COMPOSE_CMD?=$(DOCKER_COMPOSE_ENV) $(DOCKER_COMPOSE) -p $(COMPOSE_PROJECT_NAME)
DOCKER_BUILD_ARGS:=--build-arg PYTHON_VERSION=${PYTHON_VERSION} --build-arg VERSION=${VERSION} ${EXTRA_DOCKER_BUILD_ARGS}
DOCKER_BUILD?=DOCKER_BUILDKIT=1 ${DOCKER} build ${DOCKER_BUILD_ARGS}
DOCKER_RUN?=${DOCKER} run --rm ${EXTRA_DOCKER_RUN_ARGS}

PYTHONIC_SOURCES:=$(shell find $(MODNAME) -type f -name '*.py') setup.py MANIFEST.in setup.cfg
PYTHONIC_TEST_SOURCES:=$(shell find tests -type f -name '*.py') test-requirements.txt

BUILD_ARTEFACT?=dist/$(MODNAME)-$(VERSION).tar.gz requirements.txt constraints.txt

WHEEL_FILE?=dist/$(MODNAME)-$(VERSION)-py3-none-any.whl

all: help

requirements.txt: setup.py
	$(PYTHON3) scripts/extract_requirements.py $< -o $@

constraints.txt: setup.py
	$(PYTHON3) scripts/extract_requirements.py -c $< -o $@

dist/$(MODNAME)-$(VERSION).tar.gz: dist $(PYTHONIC_SOURCES) $(PYTHONIC_TEST_SOURCES) $(EXTRA_TEST_SOURCES) $(EXTRA_SOURCES)
	$(PYTHON3) setup.py sdist $(COMPILE)

check-allow-local-wheels:
ifneq ($(ALLOW_LOCAL_WHEELS),TRUE)
ifneq ($(shell ls -A "$(topbuilddir)/wheels" 2> /dev/null),)
	$(error Wheels directory $(topbuilddir)/wheels is not empty. Set environment variable ALLOW_LOCAL_WHEELS to TRUE to allow wheels)
endif
endif

dist wheels:
	mkdir -p $@

docker-build-%: check-allow-local-wheels ${BUILD_ARTEFACT} Dockerfile wheels
	${DOCKER_BUILD} --target $* -t ${MODNAME}_$*:${BUILD_TAG} .

docker-run-%: docker-build-%
	${DOCKER_RUN} ${MODNAME}_$*:${BUILD_TAG}

# Run unit tests with docker-compose and databases
test: docker-build-unittest
	{ \
		$(DOCKER_COMPOSE_CMD) run --rm tests; \
		EXIT_CODE=$$?; \
		$(DOCKER_COMPOSE_CMD) down; \
		exit $$EXIT_CODE; \
	}

lint: docker-run-mypy docker-run-flake8

docker-run-wheel: dist
docker-run-wheel: EXTRA_DOCKER_RUN_ARGS+=--mount type=bind,source=$(realpath dist),target=/${MODNAME}/dist

$(WHEEL_FILE): docker-run-wheel

wheel: $(WHEEL_FILE)

clean:
	-rm -rf __pycache__
	-rm -rf *.egg-info
	-rm requirements.txt
	-rm constraints.txt
	-find -name __pycache__ -exec rm -r "{}" \;

help:
	@echo "${MODNAME} -- all make operations require docker"
	@echo "  make test             run unit tests"
	@echo "  make lint             lint"
	@echo "  make clean            remove temporary files"
	@echo "  make wheel            make a wheel file for distribution"


.PHONY: test lint wheel clean all help
