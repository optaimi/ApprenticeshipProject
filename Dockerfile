# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend code
# We explicitly ignore the frontend folder to keep the image small
COPY . .

# Expose the port the app runs on (As Cloud Run expects 8080 by default)
ENV PORT=8080

# Command to run the application
# We use 0.0.0.0 to ensure it listens on all interfaces within the container
CMD uvicorn api_server:app --host 0.0.0.0 --port $PORT