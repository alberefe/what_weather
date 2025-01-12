FROM python:3.11-slim

WORKDIR /app

# Create non-root user
RUN groupadd -r appusergroup && useradd -r -g appusergroup appuser

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy project files first - this is different from before
COPY . .

# Set ownership
RUN chown -R appuser:appusergroup /app

# Switch to non-root user for package installation
USER appuser

# Install uv and dependencies
RUN pip install --user uv && \
    $HOME/.local/bin/uv pip install -e .

# Create and set permissions for instance directory
USER root
RUN mkdir -p instance && chown -R appuser:appusergroup instance

# Switch back to non-root user for running the application
USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1