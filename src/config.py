import os
import json
import logging
import tempfile
import atexit
import base64 # Import base64 for decoding
from google.oauth2 import service_account
import google.cloud.aiplatform as aiplatform

logger = logging.getLogger(__name__)

def initialize_vertex_ai():
    """
    Initialize Vertex AI with project configuration and credentials.

    This function prioritizes loading credentials from a Base64 encoded string
    (expected in deployment environments like Streamlit Cloud). If that's not found,
    it falls back to loading from a file path (for local development with .env).

    Raises:
        ValueError: If essential environment variables (PROJECT_ID, GOOGLE_CREDENTIALS_B64/GOOGLE_APPLICATION_CREDENTIALS) are missing or invalid.
        RuntimeError: If credential loading or Vertex AI initialization fails.
    """
    project_id = os.getenv("PROJECT_ID")
    location = os.getenv("LOCATION", "us-central1")
    
    if not project_id:
        logger.error("PROJECT_ID environment variable is not set.")
        raise ValueError("PROJECT_ID environment variable is required. Please set it in your .env file or Streamlit secrets.")
    
    credentials = None
    temp_credentials_file_path = None

    # --- Strategy 1: Load from Base64 encoded environment variable (for Streamlit Cloud) ---
    credentials_b64 = os.getenv("GOOGLE_CREDENTIALS_B64")
    if credentials_b64:
        logger.info("GOOGLE_CREDENTIALS_B64 environment variable found. Attempting to decode and load.")
        try:
            # Decode the Base64 string
            decoded_json_bytes = base64.b64decode(credentials_b64)
            credentials_info = json.loads(decoded_json_bytes.decode('utf-8'))
            logger.info("Base64 credentials decoded and parsed successfully.")

            # Write the decoded JSON content to a temporary file
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
            logger.info("Credentials loaded from temporary file.")

        except (base64.binascii.Error, json.JSONDecodeError) as e:
            logger.critical(f"Failed to decode or parse Base64 credentials: {e}", exc_info=True)
            raise RuntimeError(f"Failed to decode or parse Base64 GOOGLE_CREDENTIALS_B64. Error: {e}")
        except Exception as e:
            logger.critical(f"An unexpected error occurred during Base64 credential handling: {e}", exc_info=True)
            raise RuntimeError(f"Failed to load Google Cloud credentials from Base64. Error: {e}")
    else:
        # --- Strategy 2: Fallback to file path (for local .env setup) ---
        credentials_file_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not credentials_file_path:
            logger.error("Neither GOOGLE_CREDENTIALS_B64 nor GOOGLE_APPLICATION_CREDENTIALS environment variable is set.")
            raise ValueError("Google Cloud credentials are required. Please set GOOGLE_CREDENTIALS_B64 (Base64 JSON) or GOOGLE_APPLICATION_CREDENTIALS (file path).")

        if not os.path.exists(credentials_file_path):
            logger.error(f"GOOGLE_APPLICATION_CREDENTIALS path does not exist: {credentials_file_path}")
            raise ValueError(f"GOOGLE_APPLICATION_CREDENTIALS file not found at: {credentials_file_path}")
        
        try:
            credentials = service_account.Credentials.from_service_account_file(credentials_file_path)
            logger.info(f"Credentials loaded from file path: {credentials_file_path}")
        except Exception as e:
            logger.critical(f"Failed to load Google Cloud credentials from file path: {e}", exc_info=True)
            raise RuntimeError(f"Failed to load Google Cloud credentials from file. Error: {e}")

    logger.info(f"Attempting to initialize Vertex AI for project '{project_id}' in location '{location}'.")
    try:
        aiplatform.init(
            project=project_id,
            location=location,
            credentials=credentials
        )
        logger.info("Vertex AI SDK initialized successfully.")
    except Exception as e:
        logger.critical(f"Failed to initialize Vertex AI SDK with project '{project_id}' and location '{location}': {e}", exc_info=True)
        raise RuntimeError(f"Failed to initialize Vertex AI SDK. Check your project ID, location, and authentication. Error: {e}")

# The rest of the functions (get_project_config, get_model_config) remain the same
def get_project_config():
    project_id = os.getenv("PROJECT_ID")
    location = os.getenv("LOCATION", "us-central1")
    if not project_id:
        logger.error("PROJECT_ID environment variable is not set when attempting to get project config.")
        raise ValueError("PROJECT_ID environment variable is required. Please set it in your .env file.")
    logger.debug(f"Retrieved project config: Project ID='{project_id}', Location='{location}'")
    return project_id, location

def get_model_config():
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
