FROM python:3.11-slim

WORKDIR /app

# Upgrade pip for security
RUN pip install --no-cache-dir --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ /app/src/

# Set non-root user for security (good practice for DevSecOps)
RUN useradd -m appuser
USER appuser

EXPOSE 8080

# Run with Gunicorn for production-like environment or direct python
CMD ["python", "-m", "src.main"]
