# Base image: Official lightweight Python 3.14 slim image
FROM python:3.14-slim

# Prevent Python from writing .pyc files and buffer logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Working directory inside container
WORKDIR /app

# Security: Create non-root system user and group
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/sh -m appuser

# Leverage Docker layer caching: install dependencies before copying app source
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code with non-root ownership
COPY --chown=appuser:appgroup ./app ./app

# Run as non-privileged user
USER appuser

# Expose microservice port
EXPOSE 8000

# Single source of health-check truth
HEALTHCHECK --interval=15s --timeout=5s --start-period=5s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=3)"

# Start Uvicorn bound to 0.0.0.0
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
