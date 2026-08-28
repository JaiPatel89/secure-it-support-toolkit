# ============================================================
# SYSTEM INFORMATION TESTS
# ============================================================
# This test module verifies the functionality of system_info.py.
#
# The tests check that:
#
# - System information is returned correctly.
# - The operating system is detected.
# - The hostname is retrieved.
# - The operating system version is identified.
# - The system architecture is identified.
# - The processor information is retrieved.
# - The username is retrieved.
# - RAM information is calculated.
# - Disk usage information is included.
#
# External system information is mocked where appropriate so
# that the tests produce predictable results.
#
# This allows the tests to run consistently without depending
# on the actual configuration of the computer running pytest.
# ============================================================


# ============================================================
# MODULE IMPORTS
# ============================================================
# SimpleNamespace:
#     Creates simple mock objects for testing.
#
# psutil:
#     Used to mock system resource information.
#
# platform:
#     Used to mock operating system information.
#
# socket:
#     Used to mock hostname information.
#
# getpass:
#     Used to mock the current username.
# ============================================================

from types import SimpleNamespace

import psutil
import platform
import socket
import getpass


# ============================================================
# IMPORT SYSTEM INFORMATION MODULE
# ============================================================
# The src directory is added to sys.path by the existing test
# configuration used by the project.
# ============================================================

from system_info import get_system_information


# ============================================================
# TEST SYSTEM INFORMATION
# ============================================================
# Verifies that the module returns the expected system
# information when the operating system functions are mocked.
# ============================================================

def test_system_information(monkeypatch):

    # --------------------------------------------------------
    # Mock operating system information.
    # --------------------------------------------------------

    monkeypatch.setattr(
        platform,
        "system",
        lambda: "Windows"
    )

    monkeypatch.setattr(
        platform,
        "version",
        lambda: "10.0.22631"
    )

    monkeypatch.setattr(
        platform,
        "architecture",
        lambda: ("64bit", "WindowsPE")
    )

    monkeypatch.setattr(
        platform,
        "processor",
        lambda: "Test Processor"
    )


    # --------------------------------------------------------
    # Mock hostname.
    # --------------------------------------------------------

    monkeypatch.setattr(
        socket,
        "gethostname",
        lambda: "TEST-PC"
    )


    # --------------------------------------------------------
    # Mock username.
    # --------------------------------------------------------

    monkeypatch.setattr(
        getpass,
        "getuser",
        lambda: "TestUser"
    )


    # --------------------------------------------------------
    # Mock RAM information.
    #
    # 16 GB total memory is provided for the test.
    # --------------------------------------------------------

    fake_memory = SimpleNamespace(
        total=16 * (1024 ** 3)
    )

    monkeypatch.setattr(
        psutil,
        "virtual_memory",
        lambda: fake_memory
    )


    # --------------------------------------------------------
    # Mock disk usage.
    #
    # 500 GB total with 200 GB used.
    # --------------------------------------------------------

    fake_disk = SimpleNamespace(
        total=500 * (1024 ** 3),
        used=200 * (1024 ** 3),
        free=300 * (1024 ** 3),
        percent=40.0
    )

    monkeypatch.setattr(
        psutil,
        "disk_usage",
        lambda path: fake_disk
    )


    # --------------------------------------------------------
    # Run the system information function.
    # --------------------------------------------------------

    result = get_system_information()


    # --------------------------------------------------------
    # Verify operating system.
    # --------------------------------------------------------

    assert result["Operating System"] == "Windows"


    # --------------------------------------------------------
    # Verify operating system version.
    # --------------------------------------------------------

    assert result["OS Version"] == "10.0.22631"


    # --------------------------------------------------------
    # Verify hostname.
    # --------------------------------------------------------

    assert result["Hostname"] == "TEST-PC"


    # --------------------------------------------------------
    # Verify architecture.
    # --------------------------------------------------------

    assert result["Architecture"] == "64bit"


    # --------------------------------------------------------
    # Verify processor.
    # --------------------------------------------------------

    assert result["Processor"] == "Test Processor"


    # --------------------------------------------------------
    # Verify username.
    # --------------------------------------------------------

    assert result["Username"] == "TestUser"


    # --------------------------------------------------------
    # Verify RAM.
    # --------------------------------------------------------

    assert "16" in str(result["RAM"])


    # --------------------------------------------------------
    # Verify disk usage.
    #
    # The system_info module reports disk usage using the
    # format:
    #
    # "200.00 GB used of 500.00 GB"
    # --------------------------------------------------------

    assert "200.00 GB used" in result["Disk Usage"]

    assert "500.00 GB" in result["Disk Usage"]


# ============================================================
# TEST HOSTNAME ERROR
# ============================================================
# Verifies that the module handles an error retrieving the
# hostname without crashing.
# ============================================================

def test_hostname_error(monkeypatch):

    monkeypatch.setattr(
        platform,
        "system",
        lambda: "Windows"
    )

    monkeypatch.setattr(
        platform,
        "version",
        lambda: "Test Version"
    )

    monkeypatch.setattr(
        platform,
        "architecture",
        lambda: ("64bit", "WindowsPE")
    )

    monkeypatch.setattr(
        platform,
        "processor",
        lambda: "Test Processor"
    )

    monkeypatch.setattr(
        socket,
        "gethostname",
        lambda: (_ for _ in ()).throw(
            Exception("Hostname error")
        )
    )


    monkeypatch.setattr(
        getpass,
        "getuser",
        lambda: "TestUser"
    )


    fake_memory = SimpleNamespace(
        total=8 * (1024 ** 3)
    )

    monkeypatch.setattr(
        psutil,
        "virtual_memory",
        lambda: fake_memory
    )


    fake_disk = SimpleNamespace(
        percent=50.0
    )

    monkeypatch.setattr(
        psutil,
        "disk_usage",
        lambda path: fake_disk
    )


    result = get_system_information()


    assert "Hostname" in result


# ============================================================
# TEST RAM ERROR
# ============================================================
# Verifies that the module handles a failure when retrieving
# memory information.
# ============================================================

def test_ram_error(monkeypatch):

    monkeypatch.setattr(
        psutil,
        "virtual_memory",
        lambda: (_ for _ in ()).throw(
            Exception("Memory error")
        )
    )


    result = get_system_information()


    assert "RAM" in result


# ============================================================
# TEST DISK ERROR
# ============================================================
# Verifies that the module handles a failure when retrieving
# disk information.
# ============================================================

def test_disk_error(monkeypatch):

    monkeypatch.setattr(
        psutil,
        "disk_usage",
        lambda path: (_ for _ in ()).throw(
            Exception("Disk error")
        )
    )


    result = get_system_information()


    assert "Disk Usage" in result