import os
import subprocess
import toml
from dotenv import load_dotenv # Still useful for other .env variables if present

# Path to your .streamlit/secrets.toml file
SECRETS_TOML_PATH = os.path.join(".streamlit", "secrets.toml")

# Load other environment variables from .env for local setup
# This ensures that variables not in secrets.toml but needed locally are still loaded.
load_dotenv()

print(f"Loading secrets from {SECRETS_TOML_PATH} and .env...")

# --- Load secrets from .streamlit/secrets.toml ---
try:
    with open(SECRETS_TOML_PATH, 'r') as f:
        secrets_content = f.read()
    
    parsed_secrets = toml.loads(secrets_content)

    # Set environment variables from secrets.toml
    for key, value in parsed_secrets.items():
        # Ensure the value is a string for os.environ
        os.environ[key] = str(value)
        print(f"Set environment variable: {key}")

except FileNotFoundError:
    print(f"Error: {SECRETS_TOML_PATH} not found. Please ensure it exists and contains your secrets.")
    print("For local simulation, create this file based on .streamlit/secrets.toml.example")
    exit(1)
except Exception as e:
    print(f"Error loading secrets from {SECRETS_TOML_PATH}: {e}")
    exit(1)

# At this point, GOOGLE_CREDENTIALS_B64 should be set in os.environ
# if it was present in secrets.toml. The config.py will then handle it.

print("All environment variables set. Launching Streamlit app...")

# Launch the Streamlit application
try:
    subprocess.run(["streamlit", "run", "app.py"], check=True)
except subprocess.CalledProcessError as e:
    print(f"Error running Streamlit app: {e}")
    exit(1)
