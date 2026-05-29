# Application image for the Acme Operations Agentic Assistant (build task T-0.2).
FROM python:3.12-slim

WORKDIR /app

# Install dependencies first for layer caching.
COPY pyproject.toml ./
RUN pip install --no-cache-dir .

# Copy the application source.
COPY app ./app
COPY agent ./agent
COPY mcp_server ./mcp_server
COPY skills ./skills
COPY db ./db
COPY eval ./eval
COPY observability ./observability
COPY ui ./ui

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
