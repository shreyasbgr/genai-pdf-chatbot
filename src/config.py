import os
import json
import logging
import tempfile
import atexit # For cleaning up temporary files
from google.oauth2 import service_account
import google.cloud.aiplatform as aiplatform

logger = logging.getLogger(__name__)

def initialize_vertex_ai():
    """
    Initialize Vertex AI with project configuration and credentials.

    This function attempts to load Google Cloud credentials.
    It first tries to parse the GOOGLE_APPLICATION_CREDENTIALS environment variable
    as direct JSON content (common for secure deployment platforms like Streamlit Cloud).
    If that fails, it assumes the variable contains a file path and attempts to load from there.
    For JSON content, it writes it to a temporary file and sets the env var to that path.

    Raises:
        ValueError: If essential environment variables (PROJECT_ID, GOOGLE_APPLICATION_CREDENTIALS) are missing or invalid.
        RuntimeError: If Vertex AI initialization fails due to credential issues or API access.
    """
    project_id = os.getenv("PROJECT_ID")
    location = os.getenv("LOCATION", "us-central1")
    
    if not project_id:
        logger.error("PROJECT_ID environment variable is not set.")
        raise ValueError("PROJECT_ID environment variable is required. Please set it in your .env file or Streamlit secrets.")
    
    credentials_env_var = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    if not credentials_env_var:
        logger.error("GOOGLE_APPLICATION_CREDENTIALS environment variable is not set.")
        raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable is required. "
                         "It should either be a path to your service account key file or the JSON content itself.")

    credentials = None
    temp_credentials_file_path = None # To store path of temp file if created

    try:
        # --- IMPORTANT CHANGE: .strip() added here ---
        # Attempt to parse the environment variable as JSON content first
        credentials_info = json.loads(credentials_env_var.strip()) # <--- Added .strip()
        logger.info("GOOGLE_APPLICATION_CREDENTIALS recognized as direct JSON content.")

        # Write the JSON content to a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
            json.dump(credentials_info, temp_file)
            temp_credentials_file_path = temp_file.name
        
        # Set the GOOGLE_APPLICATION_CREDENTIALS env var to point to this temporary file
        # This is crucial as Google's client libraries expect a file path.
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_credentials_file_path
        logger.info(f"Credentials written to temporary file: {temp_credentials_file_path}")

        # Register the temporary file for deletion when the program exits
        atexit.register(lambda: os.remove(temp_credentials_file_path) if os.path.exists(temp_credentials_file_path) else None)
        logger.info("Temporary credentials file registered for cleanup on exit.")

        # Load credentials from the temporary file
        credentials = service_account.Credentials.from_service_account_file(temp_credentials_file_path)

    except json.JSONDecodeError:
        # If it's not valid JSON, assume it's already a file path (for local .env setup)
        logger.info("GOOGLE_APPLICATION_CREDENTIALS is not direct JSON. Assuming it's a file path.")
        if os.path.exists(credentials_env_var):
            credentials = service_account.Credentials.from_service_account_file(credentials_env_var)
            logger.info(f"Credentials loaded from file path: {credentials_env_var}")
        else:
            logger.error(f"GOOGLE_APPLICATION_CREDENTIALS is neither valid JSON nor a valid file path: {credentials_env_var}")
            raise ValueError(f"GOOGLE_APPLICATION_CREDENTIALS must be valid JSON content or a path to a valid JSON file. Path '{credentials_env_var}' does not exist.")
    except Exception as e:
        logger.critical(f"An unexpected error occurred during credential loading or temporary file handling: {e}", exc_info=True)
        raise RuntimeError(f"Failed to load Google Cloud credentials. Error: {e}")

    logger.info(f"Attempting to initialize Vertex AI for project '{project_id}' in location '{location}'.")
    try:
        # Initialize Vertex AI SDK with the loaded credentials
        aiplatform.init(
            project=project_id,
            location=location,
            credentials=credentials # Pass the loaded credentials here
        )
        logger.info("Vertex AI SDK initialized successfully.")
    except Exception as e:
        logger.critical(f"Failed to initialize Vertex AI SDK with project '{project_id}' and location '{location}': {e}", exc_info=True)
        raise RuntimeError(f"Failed to initialize Vertex AI SDK. Check your project ID, location, and authentication. Error: {e}")

# The rest of the functions (get_project_config, get_model_config) remain the same
def get_project_config():
    """
    Get project configuration from environment variables.

    Returns:
        tuple: (project_id, location)

    Raises:
        ValueError: If PROJECT_ID environment variable is not set.
    """
    project_id = os.getenv("PROJECT_ID")
    location = os.getenv("LOCATION", "us-central1")

    if not project_id:
        logger.error("PROJECT_ID environment variable is not set when attempting to get project config.")
        raise ValueError("PROJECT_ID environment variable is required. Please set it in your .env file.")
    
    logger.debug(f"Retrieved project config: Project ID='{project_id}', Location='{location}'")
    return project_id, location

def get_model_config():
    """
    Get model configuration from environment variables.

    Returns:
        dict: Dictionary containing model configurations

    Raises:
        ValueError: If TEMPERATURE or MAX_OUTPUT_TOKENS cannot be converted to the correct type.
    """
    config = {
        "language_model": os.getenv("MODEL_NAME", "gemini-2.5-pro"),
        "embedding_model": os.getenv("EMBEDDING_MODEL", "text-embedding-004").strip(),
        "temperature": 0.0, 
        "max_output_tokens": 1024 
    }

    try:
        temp_str = os.getenv("TEMPERATURE", "0")
        config["temperature"] = float(temp_str)
        if not (0 <= config["temperature"] <= 1):
            logger.warning(f"TEMPERATURE value '{temp_str}' out of valid range (0-1). Using default 0.0. Please set a value between 0 and 1.")
            config["temperature"] = 0.0
    except ValueError:
        logger.warning(f"Invalid TEMPERATURE value '{os.getenv('TEMPERATURE')}'. Could not convert to float. Using default 0.0.")
        config["temperature"] = 0.0
    except Exception as e:
        logger.warning(f"Unexpected error retrieving TEMPERATURE: {e}. Using default 0.0.", exc_info=True)
        config["temperature"] = 0.0

    try:
        tokens_str = os.getenv("MAX_OUTPUT_TOKENS", "1024")
        config["max_output_tokens"] = int(tokens_str)
        if not (config["max_output_tokens"] > 0):
            logger.warning(f"MAX_OUTPUT_TOKENS value '{tokens_str}' is not positive. Using default 1024. Please set a positive integer.")
            config["max_output_tokens"] = 1024
    except ValueError:
        logger.warning(f"Invalid MAX_OUTPUT_TOKENS value '{os.getenv('MAX_OUTPUT_TOKENS')}'. Could not convert to int. Using default 1024.")
        config["max_output_tokens"] = 1024
    except Exception as e:
        logger.warning(f"Unexpected error retrieving MAX_OUTPUT_TOKENS: {e}. Using default 1024.", exc_info=True)
        config["max_output_tokens"] = 1024
    
    logger.debug(f"Retrieved model config: {config}")
    return config