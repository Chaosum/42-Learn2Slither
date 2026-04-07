FROM python:3.14

WORKDIR /app

# Install system dependencies for tkinter and X11
RUN apt-get update && apt-get install -y \
    python3-tk \
    x11-apps \
    libxext6 \
    libxrender1 \
    libxkbcommon0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "main.py"]
