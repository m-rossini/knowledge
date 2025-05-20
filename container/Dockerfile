FROM python:3.13-slim AS base

LABEL maintainer="Knowledge Project Maintainer"
LABEL description="Knowledge project with Wikipedia data processing"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PROMETHEUS_MULTIPROC_DIR=/tmp \
    PYTHONPATH=/app

# Install system dependencies (including libzim dependencies and zsh)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libzim-dev \
    pkg-config \
    zsh \
    openssh-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Add ll alias to zsh for all users
RUN echo 'alias ll="ls -alF --color=auto"' >> /etc/zsh/zshrc

# Create base structure with minimal layer count
RUN mkdir -p /app/data/wikipedia \
    /app/backup/wikipedia \
    /app/logs \
    /app/config

# Set working directory
WORKDIR /app

# ---------- Dependencies Stage ----------
FROM base AS dependencies

# Copy requirements first for better caching
COPY requirements.txt .

# Update pip and install Python dependencies with proper error handling
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt || \
    (echo -e "\033[0;31m>>>> Dockerfile::BuildStep Package installation failed. Check requirements.txt for errors.\033[0m" && exit 1)

# ---------- Final Stage ----------
FROM dependencies

# Copy application code - these layers change frequently
COPY config/ /app/config/
COPY scripts/ /app/scripts/
COPY src/ /app/src/

# Make scripts executable
RUN chmod +x /app/scripts/download_sources.sh

# Create volumes for data persistence
VOLUME ["/app/data", "/app/logs", "/app/backup", "/app/config"]

# Expose port for metrics endpoint (for Prometheus scraping)
EXPOSE 9091

# Set BASE_PATH for all scripts and apps
ENV BASE_PATH=/app

# Set the entrypoint to the download_sources.sh script and always pass --log-level from the environment
ENTRYPOINT ["/app/scripts/download_sources.sh", "--log-level", "${LOG_LEVEL}"]

# Default command (can be overridden)
CMD []