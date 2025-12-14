FROM python:3.11-slim

# Install system dependencies including PostGIS
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        git \
        gdal-bin \
        libgdal-dev \
        postgresql-client \
        netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create directory for static files
RUN mkdir -p /app/staticfiles

# Expose port for Django
EXPOSE 8000

# Run entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "aquawatch.wsgi:application"]
