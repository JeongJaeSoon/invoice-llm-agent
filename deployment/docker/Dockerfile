FROM python:3.12-slim AS builder

WORKDIR /app

# Install poetry and dependencies
RUN pip install --no-cache-dir poetry

# Copy only requirements files first
COPY pyproject.toml README.md ./

# Install dependencies
RUN poetry config virtualenvs.create false \
  && poetry install --only main --no-interaction --no-ansi --no-root

# Copy source files
COPY src/ src/

# Runtime stage
FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies and curl for healthcheck
RUN apt-get update \
  && apt-get install -y --no-install-recommends curl \
  && pip install --no-cache-dir "fastapi[all]" uvicorn \
  && rm -rf /root/.cache/pip \
  && rm -rf /var/lib/apt/lists/*

# Copy only necessary files from builder
COPY --from=builder /app/src /app/src
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# Set environment variables
ENV PYTHONPATH=/app \
  PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1

# Create non-root user and set permissions
RUN useradd -r -s /bin/false appuser \
  && chown -R appuser: /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
