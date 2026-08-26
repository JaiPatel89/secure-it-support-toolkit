# ============================================================
# SERVICE STATUS TESTS
# ============================================================
# This module contains automated tests for service_status.py.
#
# The tests verify that the service-status module correctly:
#
# - Detects the operating system
# - Checks Windows services
# - Checks Linux services
# - Checks macOS services
# - Standardises service status values
# - Handles missing commands
# - Handles missing services
# - Handles stopped services
# - Handles command errors
#
# subprocess.run() is mocked so the tests do not depend on
# the actual services running on the computer.
#
# This allows the tests to produce predictable results across
# different operating systems and test environments.
# ============================================================


# ============================================================
# TEST MODULE PATH
# ============================================================
# The application modules are stored inside the src directory.
#
# The project root is found using pathlib and the src directory
# is then added to Python's import path.
# ============================================================

import sys
from pathlib import Path


sys.path.insert(
    0,
    str(
        Path(__file__).resolve().parent.parent / "src"
    )
)


# ============================================================
# MODULE IMPORTS
# ============================================================
# subprocess:
#     Used so subprocess.run() can be mocked during testing.
#
# SimpleNamespace:
#     Creates simple fake subprocess results.
#
# service_status:
#     Contains the functions being tested.
# ============================================================

import subprocess

from types import SimpleNamespace

from service_status import (
    get_service_status,
    standardize_status,
    run_command
)


# ============================================================
# TEST STATUS STANDARDISATION
# ============================================================
# These tests verify that different service-status values are
# converted into a consistent format.
# ============================================================


def test_standardize_running_status():

    assert standardize_status("running") == "Running"
    assert standardize_status("active") == "Running"


def test_standardize_stopped_status():

    assert standardize_status("stopped") == "Stopped"
    assert standardize_status("inactive") == "Stopped"
    assert standardize_status("dead") == "Stopped"
    assert standardize_status("failed") == "Stopped"


def test_standardize_unknown_status():

    assert standardize_status("pending") == "Pending"


# ============================================================
# TEST WINDOWS SERVICES
# ============================================================
# Verifies that Windows service information is correctly
# retrieved and standardised.
#
# PowerShell commands are mocked so the test does not depend
# on the actual Windows services running on the computer.
# ============================================================


def test_windows_services(monkeypatch):

    monkeypatch.setattr(
        "platform.system",
        lambda: "Windows"
    )


    # --------------------------------------------------------
    # Mock PowerShell service results.
    # --------------------------------------------------------
    # The command contains the Windows service name, allowing
    # the test to return a different status for each service.
    # --------------------------------------------------------

    def fake_run(
        command,
        capture_output=True,
        text=True,
        timeout=None
    ):

        if "wuauserv" in command[-1]:

            return SimpleNamespace(
                returncode=0,
                stdout="Running\n",
                stderr=""
            )

        elif "Dnscache" in command[-1]:

            return SimpleNamespace(
                returncode=0,
                stdout="Running\n",
                stderr=""
            )

        elif "Spooler" in command[-1]:

            return SimpleNamespace(
                returncode=0,
                stdout="Stopped\n",
                stderr=""
            )

        elif "WinDefend" in command[-1]:

            return SimpleNamespace(
                returncode=0,
                stdout="Running\n",
                stderr=""
            )


        return SimpleNamespace(
            returncode=0,
            stdout="",
            stderr=""
        )


    monkeypatch.setattr(
        subprocess,
        "run",
        fake_run
    )


    result = get_service_status()


    assert result["Operating System"] == "Windows"

    assert (
        result["Services"]["Windows Update"]
        == "Running"
    )

    assert (
        result["Services"]["DNS Client"]
        == "Running"
    )

    assert (
        result["Services"]["Print Spooler"]
        == "Stopped"
    )

    assert (
        result["Services"]["Microsoft Defender"]
        == "Running"
    )


# ============================================================
# TEST WINDOWS MISSING SERVICE
# ============================================================
# An empty PowerShell result represents a service that could
# not be found.
# ============================================================


def test_windows_service_not_found(monkeypatch):

    monkeypatch.setattr(
        "platform.system",
        lambda: "Windows"
    )


    def fake_run(
        command,
        capture_output=True,
        text=True,
        timeout=None
    ):

        return SimpleNamespace(
            returncode=0,
            stdout="",
            stderr=""
        )


    monkeypatch.setattr(
        subprocess,
        "run",
        fake_run
    )


    result = get_service_status()


    for status in result["Services"].values():

        assert status == "Not Found"


# ============================================================
# TEST WINDOWS COMMAND UNAVAILABLE
# ============================================================
# Verifies that FileNotFoundError is handled by run_command().
#
# This simulates a situation where PowerShell is unavailable.
# ============================================================


def test_windows_command_unavailable(monkeypatch):

    monkeypatch.setattr(
        "platform.system",
        lambda: "Windows"
    )


    def fake_run(
        command,
        capture_output=True,
        text=True,
        timeout=None
    ):

        raise FileNotFoundError


    monkeypatch.setattr(
        subprocess,
        "run",
        fake_run
    )


    result = get_service_status()


    for status in result["Services"].values():

        assert status == "Command Unavailable"


# ============================================================
# TEST LINUX SERVICES
# ============================================================
# Verifies that Linux services are checked using systemctl.
#
# The SSH service is simulated as active and the Cron service
# is simulated as inactive.
# ============================================================


def test_linux_services(monkeypatch):

    monkeypatch.setattr(
        "platform.system",
        lambda: "Linux"
    )


    def fake_run(
        command,
        capture_output=True,
        text=True,
        timeout=None
    ):

        service_name = command[-1]


        if service_name == "ssh":

            return SimpleNamespace(
                returncode=0,
                stdout="active\n",
                stderr=""
            )


        elif service_name == "cron":

            return SimpleNamespace(
                returncode=0,
                stdout="inactive\n",
                stderr=""
            )


        return SimpleNamespace(
            returncode=0,
            stdout="",
            stderr=""
        )


    monkeypatch.setattr(
        subprocess,
        "run",
        fake_run
    )


    result = get_service_status()


    assert result["Operating System"] == "Linux"

    assert (
        result["Services"]["SSH"]
        == "Running"
    )

    assert (
        result["Services"]["Cron"]
        == "Stopped"
    )


# ============================================================
# TEST LINUX SERVICE NOT FOUND
# ============================================================
# Verifies that an empty systemctl response is handled.
# ============================================================


def test_linux_service_not_found(monkeypatch):

    monkeypatch.setattr(
        "platform.system",
        lambda: "Linux"
    )


    def fake_run(
        command,
        capture_output=True,
        text=True,
        timeout=None
    ):

        return SimpleNamespace(
            returncode=0,
            stdout="",
            stderr=""
        )


    monkeypatch.setattr(
        subprocess,
        "run",
        fake_run
    )


    result = get_service_status()


    for status in result["Services"].values():

        assert status == "Not Found"


# ============================================================
# TEST LINUX COMMAND UNAVAILABLE
# ============================================================
# Verifies that a missing systemctl command is handled.
# ============================================================


def test_linux_command_unavailable(monkeypatch):

    monkeypatch.setattr(
        "platform.system",
        lambda: "Linux"
    )


    def fake_run(
        command,
        capture_output=True,
        text=True,
        timeout=None
    ):

        raise FileNotFoundError


    monkeypatch.setattr(
        subprocess,
        "run",
        fake_run
    )


    result = get_service_status()


    for status in result["Services"].values():

        assert status == "Command Unavailable"


# ============================================================
# TEST macOS SERVICE RUNNING
# ============================================================
# macOS uses launchctl to check whether the SSH service is
# loaded.
#
# A return code of 0 represents a running service.
# ============================================================


def test_macos_service_running(monkeypatch):

    monkeypatch.setattr(
        "platform.system",
        lambda: "Darwin"
    )


    def fake_run(
        command,
        capture_output=True,
        text=True,
        timeout=None
    ):

        return SimpleNamespace(
            returncode=0,
            stdout="",
            stderr=""
        )


    monkeypatch.setattr(
        subprocess,
        "run",
        fake_run
    )


    result = get_service_status()


    assert result["Operating System"] == "Darwin"

    assert (
        result["Services"]["SSH"]
        == "Running"
    )


# ============================================================
# TEST macOS SERVICE STOPPED
# ============================================================
# A non-zero launchctl return code indicates that the service
# is not loaded or running.
# ============================================================


def test_macos_service_stopped(monkeypatch):

    monkeypatch.setattr(
        "platform.system",
        lambda: "Darwin"
    )


    def fake_run(
        command,
        capture_output=True,
        text=True,
        timeout=None
    ):

        return SimpleNamespace(
            returncode=1,
            stdout="",
            stderr=""
        )


    monkeypatch.setattr(
        subprocess,
        "run",
        fake_run
    )


    result = get_service_status()


    assert (
        result["Services"]["SSH"]
        == "Stopped"
    )


# ============================================================
# TEST run_command FILE NOT FOUND
# ============================================================
# Directly tests the helper function's handling of a missing
# operating-system command.
# ============================================================


def test_run_command_file_not_found(monkeypatch):

    def fake_run(
        command,
        capture_output=True,
        text=True,
        timeout=None
    ):

        raise FileNotFoundError


    monkeypatch.setattr(
        subprocess,
        "run",
        fake_run
    )


    result = run_command(
        ["fake-command"]
    )


    assert result is None