# ===== Step 1: Build the base image =====
FROM python:3.6.9-buster as base

# Install additional packages
RUN apt-get update \
    && apt-get install -y xvfb gosu \
    && rm -rf var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt /tmp/
COPY requirements-ml.txt /tmp/

RUN pip install -r /tmp/requirements.txt \
    && pip install -r /tmp/requirements-ml.txt \
    && pip install channels_redis==2.3.3

# ===== Step 2: Build the application =====
FROM base

# Copy entrypoint
COPY Docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Create system user for the application
RUN adduser --system --group --no-create-home --uid 1000 appuser

# Set working directory
WORKDIR /app
RUN chown appuser:appuser /app/

# Copy project
COPY --chown=appuser:appuser . /app/

ENTRYPOINT ["/entrypoint.sh"]
