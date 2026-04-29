FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt pyproject.toml /app/
RUN pip install --no-cache-dir -r requirements.txt poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Copy source code
COPY ./src /app/src
COPY ./tests /app/tests

# Default command (overridden in docker-compose for dev)
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8080"]
