FROM python:3.10-slim

WORKDIR src/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create proper directories with permissions
RUN mkdir -p /tmp/crewai_app/.mem0 && \
    chmod -R 777 /tmp/crewai_app

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Make run script executable
RUN chmod +x run.sh

# Set environment variables
ENV HOME=/tmp/crewai_app
ENV CREWAI_DATADIR=/tmp/crewai_app
ENV TMPDIR=/tmp/crewai_app
ENV TEMP=/tmp/crewai_app
ENV TMP=/tmp/crewai_app

# Expose port for Streamlit
EXPOSE 8501

# Command to run the application
CMD ["./run.sh"]