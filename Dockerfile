# Step 1: Base image using official Python 3.11 slim
FROM python:3.11-slim

# Step 2: Install Nginx, Supervisord, and system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    supervisor \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Step 3: Set working directory inside container
WORKDIR /app

# Step 4: Configure Python environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Step 5: Copy requirement files for all 3 microservices
COPY auth-service/requirements.txt ./auth-service/requirements.txt
COPY user-service/requirements.txt ./user-service/requirements.txt
COPY task-service/requirements.txt ./task-service/requirements.txt

# Step 6: Install Python dependencies for all microservices
RUN pip install --no-cache-dir \
    -r ./auth-service/requirements.txt \
    -r ./user-service/requirements.txt \
    -r ./task-service/requirements.txt

# Step 7: Copy application source code for all microservices
COPY auth-service ./auth-service
COPY user-service ./user-service
COPY task-service ./task-service

# Step 8: Copy Nginx and Supervisord configuration files
COPY nginx.conf /etc/nginx/nginx.conf
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Step 9: Expose Port 7860 (Hugging Face Spaces Default Port)
EXPOSE 7860

# Step 10: Launch Supervisord to run Nginx gateway and all 3 microservices concurrently
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
