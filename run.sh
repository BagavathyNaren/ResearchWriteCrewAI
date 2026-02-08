#!/bin/bash

# This script runs during the app startup on Hugging Face Spaces
# It creates required directories and sets permissions

# Create necessary directories with proper permissions
mkdir -p /tmp/crewai_app/.mem0
chmod -R 777 /tmp/crewai_app

# Print information for logs
echo "Created directory structure for CrewAI"
ls -la /tmp/crewai_app

# Start the Streamlit app
streamlit run src/app.py "$@"