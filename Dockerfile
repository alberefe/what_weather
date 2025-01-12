FROM python:3.11-slim

WORKDIR /app

# Create non-root user and set up home directory properly
RUN groupadd -r appusergroup && \
    useradd -r -g appusergroup -m -d /home/appuser appuser && \
    chown -R appuser:appusergroup /home/appuser

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Set ownership of application files
RUN chown -R appuser:appusergroup /app

# Switch to non-root user
USER appuser

# Create and set up pip cache directory
RUN mkdir -p /home/appuser/.cache/pip && \
    pip install --user uv && \
    PYTHONPATH=/app $HOME/.local/bin/uv pip install -e .

# Create instance directory (switch back to root temporarily)
USER root
RUN mkdir -p instance && chown -R appuser:appusergroup instance

# Switch back to non-root user
USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1