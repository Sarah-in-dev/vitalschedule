FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy dashboard code and data
COPY value_based/dashboards/ /app/dashboards/
COPY value_based/processed_data/ /app/data/
COPY value_based/models/ /app/models/

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    AWS_DEFAULT_REGION=us-east-1

# Expose port for Streamlit
EXPOSE 8501

# Command to run the application
ENTRYPOINT ["streamlit", "run", "dashboards/vbc_dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
