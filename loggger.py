import logging
import logging.config


# Load the logging configuration
logging.config.fileConfig("logging_config.ini")

# Get the logger specified in the file
logger = logging.getLogger("app")
