# Step 1: Base image using official Python 3.11 slim
FROM python:3.11-slim

# Step 2: Set application working directory inside container
WORKDIR /app

# Step 3: Configure Python environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Step 4: Copy dependency definition requirements.txt
COPY requirements.txt .

# Step 5: Install Python packages without caching
RUN pip install --no-cache-dir -r requirements.txt

# Step 6: Copy service source code and tests into container
COPY . .

# Step 7: Expose container port 8002
EXPOSE 8002

# Step 8: Entrypoint command executing user-service via Uvicorn server on port 8002
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
