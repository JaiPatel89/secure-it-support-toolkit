# ============================================================
# LOGGING CONFIGURATION MODULE
# ============================================================
# This module provides centralised logging for TechAssist.
#
# Logging allows TechAssist to record important application
# events such as:
#
# - Application startup
# - Diagnostic activity
# - Report generation
# - Errors
#
# Logs are stored in the "logs" directory.
#
# Keeping the logging configuration in its own module means
# other TechAssist modules can use the same logging system
# without duplicating configuration code.
# ============================================================


# ============================================================
# MODULE IMPORTS
# ============================================================

import logging
import os


# ============================================================
# LOGGING SETTINGS
# ============================================================

LOG_DIRECTORY = "logs"
LOG_FILE = os.path.join(
    LOG_DIRECTORY,
    "techassist.log"
)


# ============================================================
# CONFIGURE LOGGING
# ============================================================
# Creates the logs directory if it does not already exist.
#
# The logger writes:
#
# - INFO messages
# - WARNING messages
# - ERROR messages
# - CRITICAL messages
#
# A timestamp is included with each entry.
# ============================================================

def configure_logging():

    os.makedirs(
        LOG_DIRECTORY,
        exist_ok=True
    )

    logger = logging.getLogger()

    logger.setLevel(
        logging.INFO
    )

    # --------------------------------------------------------
    # Check whether TechAssist already has a file handler.
    #
    # This prevents duplicate log entries if the logging
    # configuration is called more than once.
    # --------------------------------------------------------

    for handler in logger.handlers:

        if (
            isinstance(
                handler,
                logging.FileHandler
            )
            and handler.baseFilename
            == os.path.abspath(LOG_FILE)
        ):

            return


    # --------------------------------------------------------
    # Create the TechAssist log file handler.
    # --------------------------------------------------------

    file_handler = logging.FileHandler(
        LOG_FILE,
        encoding="utf-8"
    )


    # --------------------------------------------------------
    # Define the format used for each log entry.
    # --------------------------------------------------------

    formatter = logging.Formatter(
        "%(asctime)s - "
        "%(levelname)s - "
        "%(message)s"
    )


    file_handler.setFormatter(
        formatter
    )


    # --------------------------------------------------------
    # Add the file handler to the root logger.
    # --------------------------------------------------------

    logger.addHandler(
        file_handler
    )


# ============================================================
# GET LOGGER
# ============================================================
# Returns a logger that can be used by TechAssist modules.
#
# Example:
#
# logger = get_logger(__name__)
#
# logger.info("Diagnostic started")
# ============================================================

def get_logger(name):

    return logging.getLogger(name)