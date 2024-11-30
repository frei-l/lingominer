# Use the official Python image as the base image
FROM python:3.12-slim

# Set environment variables to prevent Python from writing .pyc files
# and to ensure output is not buffered
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install Poetry
RUN pip install --no-cache-dir poetry

# Set the working directory inside the container
WORKDIR /app

# Copy the pyproject.toml and poetry.lock files to the container
COPY pyproject.toml poetry.lock* /app/

# Configure Poetry to install dependencies at the system level
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Copy the application code into the container
COPY . /app

# Expose the port that FastAPI runs on (default is 8000)
EXPOSE 7875

# Command to run the application
CMD ["python", "main.py"]
