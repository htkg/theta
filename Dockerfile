# Use the official Python image from the Docker Hub
FROM python:3.12-slim

# Set environment variables to reduce output
ENV PYTHONUNBUFFERED=1
ENV POETRY_NO_INTERACTION=1
ENV POETRY_VIRTUALENVS_CREATE=false

# Install system dependencies
RUN apt-get update -qq && apt-get install -y \
    bash \
    build-essential \
    ffmpeg \
    git \
    libffi-dev \
    libxml2-dev \
    libxslt-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Set working directory
WORKDIR /app

COPY pyproject.toml poetry.lock* /app/

# Install dependencies
RUN poetry install --no-interaction --no-ansi

COPY . /app/