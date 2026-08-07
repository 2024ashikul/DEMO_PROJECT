# Step 1: Base image using Python 3.11 slim
FROM python:3.11-slim

# Step 2: Working directory setup inside container
WORKDIR /app

# Step 3: Configure Python environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Step 4: Copy dependency definition requirements.txt
COPY requirements.txt .

# Step 5: Install Python packages without package caching
RUN pip install --no-cache-dir -r requirements.txt

# Step 6: Copy application code and tests into container
COPY . .

# Step 7: Expose container port 8003
EXPOSE 8003

# Step 8: Command to run task-service via Uvicorn server on port 8003
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]
