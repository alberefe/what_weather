# Start with a slim Python base image for minimal attack surface
FROM python:3.11-slim

# Set working directory for all subsequent operations
WORKDIR /app

# Create system group and user for security
# Using a non-root user is a security best practice
RUN groupadd -r appusergroup && useradd -r -g appusergroup appuser

# Install system dependencies in a single layer to reduce image size
# We clean up apt cache in the same step to keep the layer small
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for dependency management maybe it doesn't work. Gotta check using uv in docker
RUN pip install uv

# Copy only dependency-related files first
# This helps with Docker layer caching - if dependencies don't change,
# this layer can be reused
COPY pyproject.toml requirements.txt uv.lock ./

# Install dependencies using uv
RUN uv sync

# Copy the rest of the application
# This comes after dependency installation so changes to application code
# don't trigger re-installation of dependencies
COPY . .

# Create instance directory and set proper ownership
# This directory needs to be writable by the application
RUN mkdir -p instance && chown -R appuser:appusergroup /app

# Switch to non-root user for security
USER appuser

# Document that the container listens on port 5000
EXPOSE 5000

# Add healthcheck to help container orchestration systems monitor the application
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1