FROM python:3.12-slim

# Create a non-root user
RUN groupadd -r netverse && useradd -r -g netverse -u 1000 netverse

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy core application code
COPY . .

# Ensure the user has access to the app directory
RUN chown -R netverse:netverse /app

# Switch to non-root user
USER netverse

# Expose port
EXPOSE 8000

# Start with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
