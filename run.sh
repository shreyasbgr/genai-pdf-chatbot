#!/bin/bash

# Activate virtual environment
source .venv/bin/activate

# Check if .env file exists
if [ -f .env ]; then
    # Load environment variables from .env file
    export $(grep -v '^#' .env | xargs)
    
    # Check if GOOGLE_APPLICATION_CREDENTIALS is set and file exists
    if [ -n "$GOOGLE_APPLICATION_CREDENTIALS" ] && [ -f "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
        echo "Google Cloud credentials found at $GOOGLE_APPLICATION_CREDENTIALS"
    else
        echo "Warning: Google Cloud credentials not found or invalid path."
        echo "Please update the GOOGLE_APPLICATION_CREDENTIALS in your .env file."
    fi
    
    # Check if PROJECT_ID is set
    if [ -z "$PROJECT_ID" ]; then
        echo "Warning: PROJECT_ID not set in .env file."
        echo "Please update your .env file with your Google Cloud project ID."
    fi
else
    echo "Warning: .env file not found. Please create one with your Google Cloud configuration."
fi

# Run the Streamlit app
streamlit run app.py