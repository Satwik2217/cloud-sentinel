# 1. Use a lightweight Python 'base'
FROM python:3.11-slim

# 2. Set the 'Home' folder inside the container
WORKDIR /app

# 3. Install system dependencies (Required for some OpenEnv validation tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 4. Copy requirements first to leverage Docker cache
COPY requirements.txt .

# 5. Install the necessary tools (Pinned to requirements for stability)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 6. Copy the rest of the application files
COPY . .

# 7. Open the door (Port 7860 is standard for HF Spaces, but we'll stick to 8000 
# as per your main.py config, just ensure your HF Space is set to 8000)
EXPOSE 8000

# 8. The command to start our project automatically
# Added --workers 1 to stay within the 2 vCPU limit and ensure stability
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]