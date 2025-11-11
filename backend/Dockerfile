FROM python:3.11-slim

WORKDIR /app

# Copy backend requirements
COPY backend/requirements.txt /app/backend/
COPY pyproject.toml /app/

# Install dependencies
RUN pip install --no-cache-dir -r /app/backend/requirements.txt
RUN pip install --no-cache-dir -e /app/

# Copy backend code
COPY backend/ /app/backend/

# Copy src (needed for imports)
COPY src/ /app/src/

# Copy data (needed for progressions and PDFs)
COPY data/ /app/data/

# Set working directory to backend
WORKDIR /app/backend

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

