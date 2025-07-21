import os
from dotenv import load_dotenv
import google.cloud.aiplatform as aiplatform

# Load environment variables
load_dotenv()

def initialize_vertex_ai():
    """
    Initialize Vertex AI with project configuration.
    """
    project_id = os.getenv("PROJECT_ID")
    location = os.getenv("LOCATION", "us-central1")
    
    if not project_id:
        raise ValueError("PROJECT_ID environment variable is required. Please set it in your .env file.")
    
    # Initialize Vertex AI
    aiplatform.init(
        project=project_id,
        location=location
    )
    
    return project_id, location

def get_project_config():
    """
    Get project configuration from environment variables.
    
    Returns:
        tuple: (project_id, location)
    """
    project_id = os.getenv("PROJECT_ID")
    location = os.getenv("LOCATION", "us-central1")
    
    if not project_id:
        raise ValueError("PROJECT_ID environment variable is required. Please set it in your .env file.")
    
    return project_id, location

def get_model_config():
    """
    Get model configuration from environment variables.
    
    Returns:
        dict: Dictionary containing model configurations
    """
    return {
        "language_model": os.getenv("MODEL_NAME", "gemini-2.5-pro"),
        "embedding_model": os.getenv("EMBEDDING_MODEL", "text-embedding-004").strip(), # Default to text-embedding-004 and strip spaces
        "temperature": float(os.getenv("TEMPERATURE", "0")),
        "max_output_tokens": int(os.getenv("MAX_OUTPUT_TOKENS", "1024"))
    }