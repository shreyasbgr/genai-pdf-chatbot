import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging(log_level=logging.INFO, log_dir="logs", max_bytes=5*1024*1024, backup_count=5):
    """
    Sets up the logging configuration for the application.

    Logs will be:
    - Displayed on the console (INFO level and above).
    - Stored in rotating files in the specified log directory (INFO level and above).

    Args:
        log_level (int): The minimum logging level to capture (e.g., logging.INFO, logging.DEBUG).
        log_dir (str): The directory where log files will be stored.
        max_bytes (int): Maximum size of each log file in bytes (default: 5MB).
        backup_count (int): Number of backup log files to keep (default: 5).
    """
    # Ensure log directory exists
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Clear existing handlers to prevent duplicate logs if called multiple times
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # Create a formatter for consistent log message format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Console Handler: for displaying logs on the terminal
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level) # Console will also show INFO and above
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File Handler: for storing logs in rotating files
    log_file_path = os.path.join(log_dir, "app.log")
    file_handler = RotatingFileHandler(
        log_file_path,
        maxBytes=max_bytes,      # Max size of log file (5 MB)
        backupCount=backup_count # Number of backup files to keep (5 files)
    )
    file_handler.setLevel(log_level) # File will also store INFO and above
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Inform about logging setup
    root_logger.info(f"Logging configured: Logs will be written to '{log_file_path}' (max {max_bytes/1024/1024}MB x {backup_count} files) and displayed on console.")