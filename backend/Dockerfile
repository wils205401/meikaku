# Pull official base image
FROM python:3.12-slim

# Enforce unbuffered I/O mode in Python (ensures python output is sent directly to standard output and available in docker logs)
ENV PYTHONUNBUFFERED=1

# Install system deps
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv by copying the binary from the official distroless Docker image
COPY --from=ghcr.io/astral-sh/uv:0.9.26 /uv /uvx /bin/

# Compie bytecode - improves startup time (at the cost of increased installation time and image size)
ENV UV_COMPILE_BYTECODE=1

# Cache mount - specifies a persistent package cache to be used during builds (only download new or changed packages during rebuild)
ENV UV_LINK_MODE=copy

# Change the working directory to the `app` directory
WORKDIR /app

# `activate` the project virtual environment
ENV PATH="/app/.venv/bin:$PATH"

COPY ./backend/pyproject.toml .
COPY ./backend/uv.lock .

# Intermediate layers - improve build times by moving transitive dependency installation into its own layer (dependencies are generally static)
# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=/backend/uv.lock,target=uv.lock \
    --mount=type=bind,source=/backend/pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

# Copy the project into the image - split COPY into multiple steps and make use of docker cache
COPY ./backend/run.sh .
COPY ./backend/alembic.ini .
COPY ./backend/alembic ./alembic
COPY ./backend/app ./app

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

EXPOSE 8000

ENTRYPOINT ["bash", "run.sh"]
