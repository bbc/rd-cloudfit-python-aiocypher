# syntax=docker/dockerfile:1.2

# Args needed for base images
ARG PYTHON_VERSION=3.6

###############################################################################
# Stage: layer
###############################################################################
FROM python:${PYTHON_VERSION} AS layer
ARG http_proxy=
ARG https_proxy=
WORKDIR /aiocypher/

# Copy in wheels if provided
COPY wheels/ ./wheels

# Install requirements
COPY requirements.txt ./

RUN --mount=type=cache,target=/root/.cache/pip --mount=type=secret,id=forgecert pip install -f ./wheels -r requirements.txt

# Copy in everything else and install the package
ARG VERSION
COPY dist/aiocypher-${VERSION}.tar.gz ./
RUN --mount=type=cache,target=/root/.cache/pip --mount=type=secret,id=forgecert tar -xvzp --strip-components=1 -f ./aiocypher-${VERSION}.tar.gz && pip install -f ./wheels -e .

# Set the default command
ENTRYPOINT []
# Install agensgraph extras as well so the tests pick them up
RUN --mount=type=cache,target=/root/.cache/pip --mount=type=secret,id=forgecert pip install -e .[agensgraph]

###############################################################################
# Stage: testdeps
###############################################################################
FROM python:${PYTHON_VERSION} AS testdeps
ARG http_proxy=
ARG https_proxy=
WORKDIR /testdeps/

# Copy in wheels if provided
COPY wheels/ ./wheels

# Install test requirements
COPY constraints.txt ./
COPY test-requirements.txt ./
RUN --mount=type=cache,target=/root/.cache/pip --mount=type=secret,id=forgecert python -m pip install -f ./wheels --user -c constraints.txt -r ./test-requirements.txt flake8 "mypy<0.900"

###############################################################################
# Stage: tests
###############################################################################
FROM layer AS tests
ARG http_proxy=
ARG https_proxy=
WORKDIR /aiocypher/

# Install test dependencies
COPY --from=testdeps /root/.local/lib/ /root/.local/lib/

ENTRYPOINT []

###############################################################################
# Stage: unittest
###############################################################################
FROM tests AS unittest
ARG http_proxy=
ARG https_proxy=
WORKDIR /aiocypher/

# Set the default command
ENTRYPOINT ["python", "-m", "unittest"]
CMD ["-v", "-f"]

###############################################################################
# Stage: flake8
###############################################################################
FROM tests AS flake8
ARG http_proxy=
ARG https_proxy=
WORKDIR /aiocypher/

# Copy in .flake8
COPY .flake8 ./

# Set the default command
ENTRYPOINT ["python", "-m", "flake8"]
CMD ["aiocypher", "tests"]

###############################################################################
# Stage: mypy
###############################################################################
FROM tests AS mypy
ARG http_proxy=
ARG https_proxy=
WORKDIR /aiocypher/

# Copy in .flake8 and setup.cfg
COPY setup.cfg ./

# Set the default command
ENTRYPOINT ["python", "-m", "mypy"]
CMD ["-p", "aiocypher"]

###############################################################################
# Stage: wheel
###############################################################################
FROM layer AS wheel
ARG http_proxy=
ARG https_proxy=
WORKDIR /aiocypher/

RUN pip install -f ./wheels -e .
COPY scripts/run_with_dir_modes.sh /
RUN chmod u+x /run_with_dir_modes.sh
ENTRYPOINT ["/run_with_dir_modes.sh", "./dist", "python", "./setup.py", "sdist", "bdist_wheel"]
