# Use a slim Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy application code
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the application port
EXPOSE 4011

# Run the application using uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "4011"]
