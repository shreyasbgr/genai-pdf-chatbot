import os
import json
import logging
import tempfile
import atexit
from google.oauth2 import service_account
import google.cloud.aiplatform as aiplatform
import base64 # Import base64 for decoding/encoding
import binascii # Import binascii for error checking

logger = logging.getLogger(__name__)

def initialize_vertex_ai():
    """
    Initialize Vertex AI with project configuration and credentials.

    This function attempts to load Google Cloud credentials.
    It prioritizes loading from a file path (for local development).
    If the GOOGLE_APPLICATION_CREDENTIALS environment variable is not a file path,
    it assumes it contains the raw JSON content of the service account key,
    writes this content to a temporary file, and then loads credentials from there.
    Includes a robust fix for private_key newline issues if encountered.

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
    temp_credentials_file_path = None

    try:
        # --- Attempt 1: Load from file path (for local .env setup) ---
        if os.path.exists(credentials_env_var):
            credentials = service_account.Credentials.from_service_account_file(credentials_env_var)
            logger.info(f"Credentials loaded from file path: {credentials_env_var}")
        else:
            # --- Attempt 2: Assume it's direct JSON content (for Streamlit Cloud secrets) ---
            logger.info("GOOGLE_APPLICATION_CREDENTIALS is not a file path. Attempting to parse as JSON content.")
            
            # Strip whitespace to clean the string before JSON parsing
            clean_credentials_json_string = credentials_env_var.strip()

            try:
                credentials_info = json.loads(clean_credentials_json_string)
                logger.info("Credentials JSON parsed successfully from environment variable.")
                
                # Write the parsed JSON content to a temporary file
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
                    json.dump(credentials_info, temp_file) # Use json.dump to ensure correct formatting
                    temp_credentials_file_path = temp_file.name
                
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_credentials_file_path
                logger.info(f"Credentials written to temporary file: {temp_credentials_file_path}")
                atexit.register(lambda: os.remove(temp_credentials_file_path) if os.path.exists(temp_credentials_file_path) else None)
                
                credentials = service_account.Credentials.from_service_account_file(temp_credentials_file_path)
                logger.info("Credentials loaded from temporary file.")

            except json.JSONDecodeError as e_json:
                logger.warning(f"Failed to parse GOOGLE_APPLICATION_CREDENTIALS as JSON directly: {e_json}")
                # This is the persistent error. Let's try a specific fix for private_key newlines.
                
                # Attempt to manually fix private_key if it's causing issues
                # This is a heuristic based on common problems with private_key in env vars
                try:
                    # First, try to extract the private_key part as a string
                    # This is a very fragile parse, assuming the structure is mostly intact.
                    # A better way would be to get the original JSON from the user and ensure it's minified correctly.
                    
                    # Search for the private_key field and its value
                    pk_start_marker = '"private_key": "'
                    pk_end_marker = '",' # Assuming it ends with a comma and double quote
                    
                    if pk_start_marker in clean_credentials_json_string:
                        pk_start_index = clean_credentials_json_string.find(pk_start_marker) + len(pk_start_marker)
                        pk_end_index = clean_credentials_json_string.find(pk_end_marker, pk_start_index)
                        
                        if pk_end_index != -1:
                            raw_private_key_value = clean_credentials_json_string[pk_start_index:pk_end_index]
                            
                            # Check if the private key looks like it's missing newlines
                            if "-----BEGIN PRIVATE KEY-----" in raw_private_key_value and "-----END PRIVATE KEY-----" in raw_private_key_value:
                                # Remove all spaces and newlines that might have been introduced
                                cleaned_pk = raw_private_key_value.replace(' ', '').replace('\\n', '')
                                
                                # Re-insert newlines after BEGIN/END markers and every 64 chars
                                # This is a common requirement for PEM format
                                re_formatted_pk = cleaned_pk.replace("-----BEGINPRIVATEKEY-----", "-----BEGIN PRIVATE KEY-----\n")
                                re_formatted_pk = re_formatted_pk.replace("-----ENDPRIVATEKEY-----", "\n-----END PRIVATE KEY-----")
                                
                                # Insert newlines every 64 characters for the base64 content
                                key_content = re_formatted_pk.split("-----BEGIN PRIVATE KEY-----\n")[1].split("\n-----END PRIVATE KEY-----")[0]
                                formatted_key_content = '\n'.join([key_content[i:i+64] for i in range(0, len(key_content), 64)])
                                
                                final_private_key = f"-----BEGIN PRIVATE KEY-----\n{formatted_key_content}\n-----END PRIVATE KEY-----"
                                
                                # Reconstruct the JSON with the fixed private_key
                                # This is still fragile if other parts of JSON are malformed
                                credentials_info = json.loads(clean_credentials_json_string.replace(raw_private_key_value, final_private_key))
                                
                                logger.info("Private key format potentially fixed and JSON re-parsed.")
                                
                                # Retry writing to temp file and loading
                                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
                                    json.dump(credentials_info, temp_file)
                                    temp_credentials_file_path = temp_file.name
                                
                                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_credentials_file_path
                                logger.info(f"Credentials written to temporary file (fixed private key): {temp_credentials_file_path}")
                                atexit.register(lambda: os.remove(temp_credentials_file_path) if os.path.exists(temp_credentials_file_path) else None)
                                
                                credentials = service_account.Credentials.from_service_account_file(temp_credentials_file_path)
                                logger.info("Credentials loaded from temporary file (fixed private key).")
                            else:
                                # Private key markers not found or not in expected format for auto-fix
                                logger.error("Private key markers not found for auto-fix. Re-raising original JSONDecodeError.")
                                raise e_json # Re-raise original error if fix not applicable
                        else:
                            logger.error("Private key end marker not found. Re-raising original JSONDecodeError.")
                            raise e_json
                    else:
                        logger.error("Private key start marker not found. Re-raising original JSONDecodeError.")
                        raise e_json

                except Exception as e_fix:
                    logger.error(f"Attempt to fix private_key format failed: {e_fix}", exc_info=True)
                    # If fixing fails, re-raise the original JSONDecodeError
                    raise e_json # Re-raise the original JSONDecodeError

            except Exception as e:
                # Catch any other unexpected errors during the direct JSON parsing or temporary file handling
                logger.critical(f"An unexpected error occurred during direct JSON parsing or temporary file handling: {e}", exc_info=True)
                raise RuntimeError(f"Failed to load Google Cloud credentials. Error: {e}")

    except Exception as e:
        # Catch any errors from the initial file path check or the broader credential loading process
        logger.critical(f"An error occurred during initial credential path check or primary loading attempt: {e}", exc_info=True)
        raise RuntimeError(f"Failed to load Google Cloud credentials. Error: {e}")

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