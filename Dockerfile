FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash --uid 1000 botuser

# Set working directory
WORKDIR /app

# Copy requirements first for better layer caching
COPY app/requirements.txt ./app/

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r app/requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs receipts && \
    chown -R botuser:botuser /app

# Switch to non-root user
USER botuser

# Expose port for health checks
EXPOSE 8080

# Health check that actually verifies the bot can initialize
HEALTHCHECK --interval=30s --timeout=15s --start-period=60s --retries=3 \
    CMD python -c "from app.config.settings import config; config.validate()" || exit 1

# Set Python path
ENV PYTHONPATH=/app

# Run the enterprise bot
CMD ["python", "run_bot.py"]
