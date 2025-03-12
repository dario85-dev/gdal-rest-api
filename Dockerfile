FROM ghcr.io/osgeo/gdal:ubuntu-full-latest

LABEL org.opencontainers.image.description="FastAPI application to serve GDAL operations"

# Set working directory
WORKDIR /app

# Install Python and dependencies
RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-venv python3-dev libffi-dev gcc build-essential && \
    rm -rf /var/lib/apt/lists/*  # Clean up to reduce image size

# Create a virtual environment
RUN python3 -m venv /venv

# Activate virtual environment and install dependencies
ENV PATH="/venv/bin:$PATH"
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy application files
COPY app /app

# Expose API port
EXPOSE 8000

# Run FastAPI server using the virtual environment
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
