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
COPY requirements ./
COPY pyproject.toml ./
COPY uv.lock ./
COPY . .

# Set ownership of application files and ensure the appuser has write permissions
RUN chown -R appuser:appusergroup /app

# Ensure the 'instance' directory and database have proper ownership and permissions
RUN chown -R appuser:appusergroup /app/instance && \
    chmod -R u+w /app/instance

# Set permissions for the specific SQLite database file
RUN chown appuser:appusergroup /app/instance/what_weather.sqlite && \
    chmod u+w /app/instance/what_weather.sqlite

# Switch to non-root user
USER appuser

# Create and set up pip cache directory and install uv
RUN mkdir -p /home/appuser/.cache/pip && \
    pip install --user uv

# Create virtual environment using uv and install dependencies
RUN $HOME/.local/bin/uv venv && \
    . .venv/bin/activate && \
    $HOME/.local/bin/uv pip install -e .

# Set environment variable for the virtual environment
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Create instance directory (switch back to root temporarily if needed)
USER root
RUN mkdir -p instance && chown -R appuser:appusergroup instance

# Switch back to non-root user
USER appuser

# Set the environment variable for Flask
ENV FLASK_APP=what_weather

# Expose the app's port
EXPOSE 5000

# Command to run the app from __init__.py
CMD ["python", "-m", "what_weather"]

# Healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1
