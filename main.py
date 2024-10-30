# main.py
import logging

from ai_integration.ai_module import main_int_ai
from database.db_setup import main_int_db
from ui.gui import main_int_ui
from utilities.load_env import load_environment
from utilities.logger_setup import setup_logger

logger = logging.getLogger(__name__)  # Reuse the global logger


def main():

    # Initialize the logger first
    setup_logger()

    # Load the environment variables
    try:
        load_environment()
    except ValueError as e:
        logger.error(f"Error loading environment: {e}")
        print(f"Error: {e}")

    # Initialize Database
    main_int_db()

    # Initialize AI Integration
    main_int_ai()

    # Initialize UI
    main_int_ui()


if __name__ == "__main__":
    main()
