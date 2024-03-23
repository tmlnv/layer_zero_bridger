# Use the official Python image with your version
FROM python:3.11-slim

# Set the working directory in the Docker container
WORKDIR /app

# Install curl and make it available
RUN apt-get update && apt-get install -y curl

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"

# Copy the pyproject.toml and poetry.lock files
COPY pyproject.toml poetry.lock* /app/

# Disable virtualenv creation by Poetry (as the Docker container acts as a virtual environment)
RUN poetry config virtualenvs.create false

# Install project dependencies using Poetry
RUN poetry install --no-dev

# Copy the rest of application code
COPY . /app

# Set the entrypoint to the application script
ENTRYPOINT ["python", "main.py"]
