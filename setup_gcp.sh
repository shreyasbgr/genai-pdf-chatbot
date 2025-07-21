#!/bin/bash

# Script to help set up Google Cloud credentials for the PDF chatbot

echo "PDF Chatbot with Vertex AI - Google Cloud Setup"
echo "=============================================="
echo

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "Google Cloud SDK (gcloud) is not installed."
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if user is logged in
echo "Checking Google Cloud authentication..."
gcloud auth list --filter=status:ACTIVE --format="value(account)" > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "You are not logged in to Google Cloud. Please login:"
    gcloud auth login
fi

# Get the current project
current_project=$(gcloud config get-value project 2>/dev/null)
echo "Current Google Cloud project: $current_project"
echo

# Ask if user wants to use a different project
read -p "Do you want to use a different project? (y/n): " change_project
if [[ $change_project == "y" || $change_project == "Y" ]]; then
    # List available projects
    echo "Available projects:"
    gcloud projects list --format="table(projectId,name)"
    echo
    
    # Ask for project ID
    read -p "Enter the project ID you want to use: " project_id
    gcloud config set project $project_id
    current_project=$project_id
fi

# Check if Vertex AI API is enabled
echo "Checking if Vertex AI API is enabled..."
api_enabled=$(gcloud services list --project $current_project --filter="name:aiplatform.googleapis.com" --format="value(name)")
if [ -z "$api_enabled" ]; then
    echo "Vertex AI API is not enabled. Enabling now..."
    gcloud services enable aiplatform.googleapis.com --project $current_project
    echo "Vertex AI API enabled."
else
    echo "Vertex AI API is already enabled."
fi

# Create service account if needed
read -p "Do you want to create a new service account for this application? (y/n): " create_sa
if [[ $create_sa == "y" || $create_sa == "Y" ]]; then
    # Get service account name
    read -p "Enter a name for the service account (e.g., pdf-chatbot): " sa_name
    
    # Create service account
    echo "Creating service account $sa_name..."
    gcloud iam service-accounts create $sa_name \
        --display-name="PDF Chatbot Service Account" \
        --project=$current_project
    
    # Grant necessary roles
    echo "Granting Vertex AI User role..."
    gcloud projects add-iam-policy-binding $current_project \
        --member="serviceAccount:$sa_name@$current_project.iam.gserviceaccount.com" \
        --role="roles/aiplatform.user"
    
    # Create and download key
    echo "Creating and downloading service account key..."
    mkdir -p keys
    gcloud iam service-accounts keys create keys/$sa_name-key.json \
        --iam-account=$sa_name@$current_project.iam.gserviceaccount.com
    
    # Update .env file
    echo "Updating .env file..."
    echo "GOOGLE_APPLICATION_CREDENTIALS=keys/$sa_name-key.json" > .env
    echo "PROJECT_ID=$current_project" >> .env
    echo "LOCATION=us-central1" >> .env
    
    echo "Service account created and .env file updated."
    echo "Key file saved to: keys/$sa_name-key.json"
else
    # Just update the .env file with the project ID
    echo "Updating .env file with current project..."
    if [ -f .env ]; then
        # Update existing .env file
        grep -q "PROJECT_ID=" .env && \
            sed -i '' "s/PROJECT_ID=.*/PROJECT_ID=$current_project/" .env || \
            echo "PROJECT_ID=$current_project" >> .env
        
        grep -q "LOCATION=" .env || echo "LOCATION=us-central1" >> .env
    else
        # Create new .env file
        echo "PROJECT_ID=$current_project" > .env
        echo "LOCATION=us-central1" >> .env
        echo "# Set your GOOGLE_APPLICATION_CREDENTIALS path here:" >> .env
        echo "# GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account-key.json" >> .env
    fi
    
    echo ".env file updated with project ID: $current_project"
    echo "Please manually set your GOOGLE_APPLICATION_CREDENTIALS in the .env file."
fi

echo
echo "Setup complete!"
echo "You can now run the application with: ./run.sh"