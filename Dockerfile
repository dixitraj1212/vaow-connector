# Stage 1: Build the Python application with dependencies
FROM python:3.9 AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev

# Set working directory
WORKDIR /app

# Copy requirements.txt and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy the Python script and DBC file to the container
COPY main.py ./

# Stage 2: Create the lightweight deployment image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy the Python application from the builder stage
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY main.py main.dbc ./

# Install additional dependencies if needed
# Example: RUN apt-get update && apt-get install -y --no-install-recommends <package-name>

# Run the Python consumer
CMD ["python", "main.py"]
