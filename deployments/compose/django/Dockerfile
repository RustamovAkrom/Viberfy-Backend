FROM python:3.10-slim-bookworm

# Set environment variables to ensure UTF-8 encoding
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VIRTUALENVS_CREATE=false

# Update and install necessary packages for psycopg2 and Celery
RUN apt update && \
    apt install -y --no-install-recommends \
        gettext \
        libpq-dev \
        build-essential \
        curl \
        git \
        ca-certificates && \
    apt clean && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install base Python dependencies
RUN pip install --upgrade pip --default-timeout=100 && \
    pip install gunicorn uvicorn[standard] psycopg2-binary --default-timeout=100

# Set working directory
WORKDIR /app

# Copy only requirements first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt
RUN --mount=type=cache,id=custom-pip,target=/root/.cache/pip \
    pip install -r /app/requirements.txt

# Copy application scripts
COPY ./deployments/compose/django/entrypoint /entrypoint
COPY ./deployments/compose/django/start /start
COPY ./deployments/compose/django/celery/worker/start /start-celeryworker
COPY ./deployments/compose/django/celery/beat/start /start-celerybeat
COPY ./deployments/compose/django/celery/flower/start /start-flower

# Fix Windows line endings and make scripts executable
RUN for f in /start /entrypoint /start-celeryworker /start-celerybeat /start-flower; do \
        sed -i 's/\r$//g' $f && chmod +x $f; \
    done

# Copy the rest of the application code
COPY . /app

# Entrypoint
ENTRYPOINT ["/entrypoint"]

# FROM python:3.10-slim-bookworm

# # Set environment variables to ensure UTF-8 encoding
# ENV PYTHONUNBUFFERED=1 \
#     PYTHONDONTWRITEBYTECODE=1 \
#     LANG=C.UTF-8 \
#     LC_ALL=C.UTF-8

# # Update and install necessary packages
# RUN apt update && \
#     apt upgrade -y && \
#     apt install -y gettext && \
#     apt clean && rm -rf /var/lib/apt/lists/*

# # Install other Python dependencies
# RUN pip install --upgrade pip gunicorn uvicorn[standard] --default-timeout=100

# # Copy scripts and set permissions
# COPY ./deployments/compose/django/celery/worker/start /start-celeryworker
# COPY ./deployments/compose/django/celery/beat/start /start-celerybeat
# COPY ./deployments/compose/django/celery/flower/start /start-flower
# COPY ./deployments/compose/django/entrypoint /entrypoint
# COPY ./deployments/compose/django/start /start

# # Copy and set permissions for celery worker start script
# COPY ./deployments/compose/django/celery/worker/start /start-celeryworker
# RUN sed -i 's/\r$//g' /start-celeryworker && \
#    chmod +x /start-celeryworker

# # Copy and set permissions for celery beat start script
# COPY ./deployments/compose/django/celery/beat/start /start-celerybeat
# RUN sed -i 's/\r$//g' /start-celerybeat && \
#    chmod +x /start-celerybeat

# # Copy and set permissions for flower start script
# COPY ./deployments/compose/django/celery/flower/start /start-flower
# RUN sed -i 's/\r$//g' /start-flower && \
#    chmod +x /start-flower

# # Copy and set permissions for entrypoint script
# COPY ./deployments/compose/django/entrypoint /entrypoint
# RUN sed -i 's/\r$//g' /entrypoint && \
#     chmod +x /entrypoint

# # Copy and set permissions for start script
# COPY ./deployments/compose/django/start /start
# RUN sed -i 's/\r$//g' /start && \
#     chmod +x /start

# # Set working directory
# WORKDIR /app

# # Copy requirements file and install dependencies
# COPY ./requirements.txt /app/requirements.txt
# RUN --mount=type=cache,id=custom-pip,target=/root/.cache/pip \
#     pip install -r /app/requirements.txt

# # Copy the application code
# COPY . /app

# ENTRYPOINT ["/entrypoint"]
