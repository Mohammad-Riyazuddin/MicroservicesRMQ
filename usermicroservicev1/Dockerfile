# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8000 for FastAPI
EXPOSE 8000

# Define environment variable for RabbitMQ (assuming it's set in the environment or through Docker Compose)
ENV RABBITMQ_HOST=rabbitmq

# Run the application using Uvicorn (FastAPI ASGI server)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
