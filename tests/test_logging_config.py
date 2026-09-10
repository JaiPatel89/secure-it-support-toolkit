# ============================================================
# LOGGING CONFIGURATION TESTS
# ============================================================
# Tests the centralised logging configuration used by
# TechAssist.
# ============================================================


# ============================================================
# MODULE IMPORTS
# ============================================================

import sys
from pathlib import Path

sys.path.insert(
    0,
    str(
        Path(__file__).resolve().parents[1]
        / "src"
    )
)

import logging

from logging_config import (
    configure_logging,
    get_logger
)


# ============================================================
# TEST CONFIGURE LOGGING
# ============================================================
# Verifies that:
#
# - The logs directory is created.
# - The log file can be created.
# - Logging can write an entry to the file.
# ============================================================

def test_configure_logging(
    tmp_path,
    monkeypatch
):

    # --------------------------------------------------------
    # Change the working directory to pytest's temporary
    # directory.
    # --------------------------------------------------------

    monkeypatch.chdir(
        tmp_path
    )


    # --------------------------------------------------------
    # Configure logging.
    # --------------------------------------------------------

    configure_logging()


    # --------------------------------------------------------
    # Verify that the logs directory exists.
    # --------------------------------------------------------

    log_directory = (
        tmp_path
        / "logs"
    )

    assert log_directory.exists()

    # --------------------------------------------------------
    # Define the expected log file.
    # --------------------------------------------------------

    log_file = (
        log_directory
        / "techassist.log"
    )

    # --------------------------------------------------------
    # Write a test log message.
    # --------------------------------------------------------

    logger = logging.getLogger(
        "test_logging"
    )

    logger.info(
        "Test log message"
    )


    # --------------------------------------------------------
    # Make sure the logging system has written pending
    # messages to the file.
    # --------------------------------------------------------

    for handler in logging.getLogger().handlers:

        handler.flush()


    # --------------------------------------------------------
    # Verify that the log file was created.
    # --------------------------------------------------------

    assert log_file.exists()


    # --------------------------------------------------------
    # Read the log file.
    # --------------------------------------------------------

    log_contents = log_file.read_text(
        encoding="utf-8"
    )


    # --------------------------------------------------------
    # Verify the test message was written.
    # --------------------------------------------------------

    assert (
        "Test log message"
        in log_contents
    )


# ============================================================
# TEST GET LOGGER
# ============================================================
# Verifies that get_logger() returns a Python logger.
# ============================================================

def test_get_logger():

    logger = get_logger(
        "TechAssist"
    )


    assert isinstance(
        logger,
        logging.Logger
    )


    assert (
        logger.name
        == "TechAssist"
    )