import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Log format
    handlers=[
        logging.StreamHandler()  # Print logs to console
    ]
)

# Create logger instance
logger = logging.getLogger("FastAPI-App")
