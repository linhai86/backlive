################################################################################
# Build dev
################################################################################
FROM python:3.13-bookworm AS dev

ARG UID
ARG GID

# Create a group with GID if the GID doesn't exist
RUN groupadd --gid ${GID} dev > /dev/null 2>&1 ||:
# Create a user with the UID and GID
RUN useradd -m -u ${UID} -g ${GID} -s /bin/bash dev

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

ENV SOURCE_DIR=/app
ENV UV_PROJECT_ENVIRONMENT=/venv

WORKDIR ${SOURCE_DIR}

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

# Copy the project into the image
ADD --chown=${UID}:${GID} . ${SOURCE_DIR}

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

RUN chown -R ${UID}:${GID} ${UV_PROJECT_ENVIRONMENT}

USER ${UID}:${GID}

################################################################################
# Build virtual env for prod
################################################################################
FROM python:3.13-bookworm AS venv_prod

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

ENV SOURCE_DIR=/app
ENV UV_PROJECT_ENVIRONMENT=/venv

WORKDIR ${SOURCE_DIR}

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev --no-editable

# Copy the project into the image
ADD . ${SOURCE_DIR}

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable

################################################################################
# Build prod
################################################################################
FROM python:3.13-bookworm AS prod

ENV SOURCE_DIR=/app
ENV UV_PROJECT_ENVIRONMENT=/venv
ENV PATH="${UV_PROJECT_ENVIRONMENT}/bin:$PATH"
ENV PYTHONPATH=${SOURCE_DIR}

WORKDIR ${SOURCE_DIR}

COPY --from=venv_prod --chown=app:app ${UV_PROJECT_ENVIRONMENT}/ ${UV_PROJECT_ENVIRONMENT}/
COPY --from=venv_prod --chown=app:app ${SOURCE_DIR}/ ${SOURCE_DIR}/
