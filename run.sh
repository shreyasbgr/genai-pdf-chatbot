#!/bin/bash

# Activate virtual environment
# Ensure your virtual environment is set up correctly, e.g., python -m venv .venv
# and requirements are installed: pip install -r requirements.txt
source .venv/bin/activate

# Check if .env file exists
if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    
    # Read each line from .env file
    # IFS='=' tells read to split by the first '='
    # -r prevents backslash escapes from being interpreted
    # The '|| true' allows the loop to continue even if the last line of the file is empty or not properly terminated
    while IFS='=' read -r key value || [ -n "$key" ]; do
        # Trim leading/trailing whitespace from the key
        key=$(echo "$key" | xargs)

        # Skip empty lines or lines that are full comments
        if [[ -z "$key" || "$key" =~ ^# ]]; then
            continue
        fi

        # Remove inline comments from the value (everything after the first # symbol)
        # and then trim leading/trailing whitespace from the result
        value_without_comment=$(echo "$value" | sed 's/\s*#.*//' | xargs)

        # Export the variable
        export "$key=$value_without_comment"
        # Optional: Print what's being exported for debugging
        # echo "Exported: $key=$value_without_comment"
    done < .env
    
    echo "Environment variables loaded."
    
    # Check if GOOGLE_APPLICATION_CREDENTIALS is set and file exists
    if [ -n "$GOOGLE_APPLICATION_CREDENTIALS" ] && [ -f "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
        echo "Google Cloud credentials path set: $GOOGLE_APPLICATION_CREDENTIALS"
    else
        echo "Warning: GOOGLE_APPLICATION_CREDENTIALS not set or file does not exist."
        echo "Please ensure GOOGLE_APPLICATION_CREDENTIALS is set correctly in your .env file and points to a valid JSON key file."
    fi
    
    # Check if PROJECT_ID is set
    if [ -z "$PROJECT_ID" ]; then
        echo "Warning: PROJECT_ID not set in .env file."
        echo "Please update your .env file with your Google Cloud project ID."
    fi
else
    echo "Error: .env file not found. Please create one with your Google Cloud configuration."
    exit 1 # Exit if .env is critical and not found
fi

echo "Starting Streamlit app..."
# Run the Streamlit app
streamlit run app.py