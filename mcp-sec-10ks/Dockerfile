# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy server code
COPY sse_server.py .
COPY server.py .

# Expose port 8080 (Cloud Run default)
EXPOSE 8080

# Set environment variable for port
ENV PORT=8080

# Run the server
CMD ["python", "sse_server.py"]
