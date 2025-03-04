# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . .

# Install system dependencies (including SQLite)
RUN apt-get update && apt-get install -y sqlite3 libsqlite3-dev && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir flask

# Expose port 5000 for Flask
EXPOSE 5000

# Initialize the database before running
RUN python -c "from FlaskApp import init_db; init_db()"

# Run the application
CMD ["python", "app.py"]
