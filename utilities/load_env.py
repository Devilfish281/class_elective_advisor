# utilities/load_env.py


import logging
import os
import re  # Added for apikey validation

from dotenv import load_dotenv

logger = logging.getLogger(__name__)  # Reuse the global logger


def load_environment():
    print("Loading Environment variables.")

    # Load environment variables from .env
    load_dotenv()

    # Confirm API Key is Loaded:
    apikey = os.getenv("OPENAI_API_KEY")
    if not apikey:
        logger.error("OPENAI_API_KEY environment variable not set")
        raise ValueError("OPENAI_API_KEY environment variable not set")

    # Validate API key
    if not re.search(r"\d", apikey):
        logger.error("OPENAI_API_KEY must contain at least one numeric character")
        raise ValueError("OPENAI_API_KEY must contain at least one numeric character")

    # API key is valid
    logger.info("API Key loaded successfully.")
    print("API Key loaded successfully.")
