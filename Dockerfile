# Use an official GDAL base image
FROM osgeo/gdal:latest

# Set working directory
WORKDIR /app

# Install Python and dependencies
RUN apt-get update && apt-get install -y python3 python3-pip \
    && pip3 install fastapi uvicorn

# Copy application files
COPY app /app

# Expose API port
EXPOSE 8000

# Run FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
