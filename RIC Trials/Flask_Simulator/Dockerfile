# Use an official Python runtime as a base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends gcc supervisor \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the ports for both Flask apps
EXPOSE 5000
EXPOSE 5001

# Copy the supervisord configuration file
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Start the supervisor to run both Flask apps
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
