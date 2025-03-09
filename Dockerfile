FROM python:3.11-slim

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc python3-dev libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

COPY alembic.ini /app/alembic.ini
COPY migrations /app/migrations
COPY alembic /app/alembic

COPY docker-entrypoint.sh /app/docker-entrypoint.sh
# Ensure entrypoint script is executable
RUN chmod +x /app/docker-entrypoint.sh

# Set the entrypoint 
ENTRYPOINT ["/app/docker-entrypoint.sh"]
