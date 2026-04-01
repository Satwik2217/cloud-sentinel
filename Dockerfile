# 1. Use a lightweight Python 'base'
FROM python:3.11-slim

# 2. Set the 'Home' folder inside the container
WORKDIR /app

# 3. Install system dependencies (Required for health checks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 4. Copy requirements and pyproject.toml first to leverage Docker cache
COPY requirements.txt pyproject.toml ./

# 5. Install the necessary tools
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 6. Copy the rest of the application files
COPY . .

# --- CRITICAL ADDITION ---
# 7. Set PYTHONPATH so Python sees the /app root as the package source.
# This fixes the "ModuleNotFoundError: No module named 'models'" error.
ENV PYTHONPATH=/app

# 8. Open the door
EXPOSE 8000

# Tells Python to look for modules starting from the /app directory
ENV PYTHONPATH=/app

# 9. The command to start our project automatically
# Pointing to server.app:app because of our new folder structure.
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]