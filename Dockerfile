FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the project files
COPY . /app/

# Set a dummy secret key to allow collectstatic to run without failing
ENV SECRET_KEY=dummy_key_for_collectstatic

# Collect static files
RUN python manage.py collectstatic --noinput

# Ensure the entrypoint is executable
RUN chmod +x /app/docker-entrypoint.sh

# Set the entrypoint to our script
ENTRYPOINT ["/app/docker-entrypoint.sh"]
