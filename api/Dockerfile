FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install ffmpeg and system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy project files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN pip install python-dotenv

# Expose FastAPI port
EXPOSE 4011

# Run the app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "4011"]
