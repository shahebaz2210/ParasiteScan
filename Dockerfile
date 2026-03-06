FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for OpenCV and others
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application code
COPY . .

# Expose port (Internal to Docker, Nginx will map to 80)
EXPOSE 5000

# Command to run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "wsgi:app"]
