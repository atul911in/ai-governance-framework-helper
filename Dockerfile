FROM python:3.11-slim

# Install system dependencies for WeasyPrint
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry==1.7.1

# Set working directory
WORKDIR /app

# Copy dependency files first for better layer caching
COPY pyproject.toml poetry.lock* ./

# Configure Poetry to not create a virtual environment inside the container
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-interaction --no-ansi --no-root

# Copy source code and data
COPY src/ ./src/
COPY data/ ./data/

# Install the project itself
RUN poetry install --no-interaction --no-ansi --only-root

# Default command runs the API server
CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
