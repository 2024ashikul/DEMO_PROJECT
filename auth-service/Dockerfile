# Step 1: Use official lightweight Python 3.11 base image
FROM python:3.11-slim

# Step 2: Set working directory inside container to /app
WORKDIR /app

# Step 3: Set environment variables to prevent Python from writing bytecode (.pyc) and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Step 4: Copy requirements file to container working directory
COPY requirements.txt .

# Step 5: Install Python dependencies without caching packages to minimize image size
RUN pip install --no-cache-dir -r requirements.txt

# Step 6: Copy application source code and tests into container
COPY . .

# Step 7: Expose port 8001 on container network interface
EXPOSE 8001

# Step 8: Define entrypoint command to run FastAPI app via Uvicorn server on port 8001
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
