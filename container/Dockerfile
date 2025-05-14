FROM python:3.13-slim

LABEL maintainer="Knowledge Project Maintainer"
LABEL description="Knowledge project with Wikipedia data processing"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PROMETHEUS_MULTIPROC_DIR=/tmp
ENV PYTHONPATH=/app

# Install system dependencies (including libzim dependencies and zsh)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libzim-dev \
    pkg-config \
    zsh \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set up directories
WORKDIR /app

# Create necessary directories
RUN mkdir -p /app/data/wikipedia \
    /app/backup/wikipedia \
    /app/logs \
    /app/config

# Copy requirements first for better caching
COPY requirements.txt .

# Update pip and install Python dependencies with proper error handling
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt || \
    (echo -e "\033[0;31m>>>> Dockerfile::BuildStep Package installation failed. Check requirements.txt for errors.\033[0m" && exit 1)

# Copy the rest of the application
COPY src/ /app/src/
COPY config/ /app/config/
COPY scripts/ /app/scripts/

# Make scripts executable
RUN chmod +x /app/scripts/update_wikipedia.sh /app/scripts/schedule_updates.sh

# Create volumes for data persistence
VOLUME ["/app/data", "/app/logs", "/app/backup", "/app/config"]

# Expose port for metrics endpoint (for Prometheus scraping)
EXPOSE 9091

# Set the entrypoint to the update_wikipedia.sh script
ENTRYPOINT ["/app/scripts/update_wikipedia.sh"]

# Default command (can be overridden)
CMD []