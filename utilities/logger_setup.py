# utilities/logger_setup.py

import logging

# Add other file to use the logger
# import logging
# logger = logging.getLogger(__name__)  # Reuse the global logger


# TODO: Log Rotation: Implement log rotation to prevent log files from growing indefinitely.
def setup_logger():
    # Set up logging globally
    logging.basicConfig(
        level=logging.INFO,  # Change to DEBUG for more detailed logs
        format="%(asctime)s %(levelname)s %(name)s:%(lineno)d %(message)s",
        handlers=[
            logging.StreamHandler(),  # Console output
            logging.FileHandler("app.log", mode="a"),  # Log file (append mode)
        ],
    )
    return logging.getLogger(__name__)  # Return the root logger for global usage
