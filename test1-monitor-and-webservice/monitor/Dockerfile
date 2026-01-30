FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    systemd \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p /var/log/rbcapp1 && \
    mkdir -p /var/tmp/rbcapp1-status && \
    mkdir -p logs

# Copy application
COPY . .

# Run the monitor service
CMD ["python", "-u", "monitor-services.py"]