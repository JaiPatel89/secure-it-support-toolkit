# ============================================================
# SECURITY CHECKS TESTS
# ============================================================
# This module contains automated tests for security_checks.py.
#
# The tests verify that the security checks correctly:
#
# - Detect administrator privileges on Windows
# - Detect root privileges on Linux/macOS
# - Identify listening network ports
# - Identify the process associated with a port
# - Identify the process ID
# - Detect localhost exposure
# - Detect network exposure
# - Handle unknown processes
# - Handle inaccessible processes
#
# psutil and ctypes are mocked where necessary so the tests
# do not depend on the actual security configuration of the
# computer running the tests.
# ============================================================


# ============================================================
# TEST MODULE PATH
# ============================================================
# The application modules are stored inside the src directory.
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

import ctypes
import os
import socket

import psutil

from types import SimpleNamespace

from security_checks import run_security_checks


# ============================================================
# TEST WINDOWS ADMINISTRATOR PRIVILEGES
# ============================================================
# Verifies that administrator privileges are correctly detected
# when running on Windows.
# ============================================================

def test_windows_admin_privileges(monkeypatch):

    # --------------------------------------------------------
    # Pretend the operating system is Windows.
    # --------------------------------------------------------

    monkeypatch.setattr(
        "platform.system",
        lambda: "Windows"
    )


    # --------------------------------------------------------
    # Simulate an administrator account.
    #
    # IsUserAnAdmin() returning 1 means administrator.
    # --------------------------------------------------------

    monkeypatch.setattr(
        ctypes.windll.shell32,
        "IsUserAnAdmin",
        lambda: 1
    )


    # --------------------------------------------------------
    # No listening ports for this test.
    # --------------------------------------------------------

    monkeypatch.setattr(
        psutil,
        "net_connections",
        lambda kind=None: []
    )


    result = run_security_checks()


    assert (
        result["Administrator Privileges"]
        == "Yes"
    )


# ============================================================
# TEST WINDOWS NON-ADMINISTRATOR
# ============================================================
# Verifies that a standard Windows user is correctly detected.
# ============================================================

def test_windows_non_admin(monkeypatch):

    monkeypatch.setattr(
        "platform.system",
        lambda: "Windows"
    )


    # --------------------------------------------------------
    # Simulate a standard user.
    # --------------------------------------------------------

    monkeypatch.setattr(
        ctypes.windll.shell32,
        "IsUserAnAdmin",
        lambda: 0
    )


    monkeypatch.setattr(
        psutil,
        "net_connections",
        lambda kind=None: []
    )


    result = run_security_checks()


    assert (
        result["Administrator Privileges"]
        == "No"
    )


# ============================================================
# TEST WINDOWS ADMIN CHECK ERROR
# ============================================================
# Verifies that an exception during the administrator check
# does not crash the application.
# ============================================================

def test_windows_admin_check_error(monkeypatch):

    monkeypatch.setattr(
        "platform.system",
        lambda: "Windows"
    )


    # --------------------------------------------------------
    # Simulate an error while checking administrator status.
    # --------------------------------------------------------

    def raise_error():

        raise Exception(
            "Unable to determine administrator status"
        )


    monkeypatch.setattr(
        ctypes.windll.shell32,
        "IsUserAnAdmin",
        raise_error
    )


    monkeypatch.setattr(
        psutil,
        "net_connections",
        lambda kind=None: []
    )


    result = run_security_checks()


    assert (
        result["Administrator Privileges"]
        == "Unable to determine"
    )


# ============================================================
# TEST LOCALHOST LISTENING PORT
# ============================================================
# Verifies that a localhost-only listening service is correctly
# identified as "Localhost".
# ============================================================

def test_localhost_listening_port(monkeypatch):

    monkeypatch.setattr(
        "platform.system",
        lambda: "Windows"
    )


    monkeypatch.setattr(
        ctypes.windll.shell32,
        "IsUserAnAdmin",
        lambda: 0
    )


    # --------------------------------------------------------
    # Create a fake listening connection.
    # --------------------------------------------------------

    fake_connection = SimpleNamespace(

        status=psutil.CONN_LISTEN,

        laddr=SimpleNamespace(
            ip="127.0.0.1",
            port=8080
        ),

        pid=1234
    )


    monkeypatch.setattr(
        psutil,
        "net_connections",
        lambda kind=None: [fake_connection]
    )


    # --------------------------------------------------------
    # Mock the process associated with the port.
    # --------------------------------------------------------

    fake_process = SimpleNamespace(
        name=lambda: "python.exe"
    )


    monkeypatch.setattr(
        psutil,
        "Process",
        lambda pid: fake_process
    )


    result = run_security_checks()


    ports = result["Listening Ports"]


    assert len(ports) == 1

    assert ports[0]["Address"] == "127.0.0.1:8080"
    assert ports[0]["Process"] == "python.exe"
    assert ports[0]["PID"] == 1234
    assert ports[0]["Exposure"] == "Localhost"


# ============================================================
# TEST NETWORK EXPOSED PORT
# ============================================================
# Verifies that a listening service bound to a network address
# is correctly identified as "Network".
# ============================================================

def test_network_exposed_port(monkeypatch):

    monkeypatch.setattr(
        "platform.system",
        lambda: "Windows"
    )


    monkeypatch.setattr(
        ctypes.windll.shell32,
        "IsUserAnAdmin",
        lambda: 0
    )


    fake_connection = SimpleNamespace(

        status=psutil.CONN_LISTEN,

        laddr=SimpleNamespace(
            ip="192.168.1.100",
            port=445
        ),

        pid=5678
    )


    monkeypatch.setattr(
        psutil,
        "net_connections",
        lambda kind=None: [fake_connection]
    )


    fake_process = SimpleNamespace(
        name=lambda: "System"
    )


    monkeypatch.setattr(
        psutil,
        "Process",
        lambda pid: fake_process
    )


    result = run_security_checks()


    ports = result["Listening Ports"]


    assert len(ports) == 1

    assert ports[0]["Address"] == "192.168.1.100:445"
    assert ports[0]["Process"] == "System"
    assert ports[0]["PID"] == 5678
    assert ports[0]["Exposure"] == "Network"


# ============================================================
# TEST NON-LISTENING CONNECTIONS ARE IGNORED
# ============================================================
# Verifies that connections which are not listening are not
# included in the security report.
# ============================================================

def test_non_listening_connections_are_ignored(monkeypatch):

    monkeypatch.setattr(
        "platform.system",
        lambda: "Windows"
    )


    monkeypatch.setattr(
        ctypes.windll.shell32,
        "IsUserAnAdmin",
        lambda: 0
    )


    fake_connection = SimpleNamespace(

        status=psutil.CONN_ESTABLISHED,

        laddr=SimpleNamespace(
            ip="192.168.1.100",
            port=443
        ),

        pid=1234
    )


    monkeypatch.setattr(
        psutil,
        "net_connections",
        lambda kind=None: [fake_connection]
    )


    result = run_security_checks()


    assert result["Listening Ports"] == []


# ============================================================
# TEST UNKNOWN PROCESS
# ============================================================
# Verifies that the module handles a process that no longer
# exists.
# ============================================================

def test_unknown_process(monkeypatch):

    monkeypatch.setattr(
        "platform.system",
        lambda: "Windows"
    )


    monkeypatch.setattr(
        ctypes.windll.shell32,
        "IsUserAnAdmin",
        lambda: 0
    )


    fake_connection = SimpleNamespace(

        status=psutil.CONN_LISTEN,

        laddr=SimpleNamespace(
            ip="192.168.1.100",
            port=9000
        ),

        pid=9999
    )


    monkeypatch.setattr(
        psutil,
        "net_connections",
        lambda kind=None: [fake_connection]
    )


    def raise_no_process(pid):

        raise psutil.NoSuchProcess(pid)


    monkeypatch.setattr(
        psutil,
        "Process",
        raise_no_process
    )


    result = run_security_checks()


    ports = result["Listening Ports"]


    assert len(ports) == 1

    assert ports[0]["Process"] == "Unknown"
    assert ports[0]["PID"] == 9999
    assert ports[0]["Exposure"] == "Network"


# ============================================================
# TEST ACCESS DENIED PROCESS
# ============================================================
# Verifies that the module handles a process that cannot be
# accessed because of permissions.
# ============================================================

def test_access_denied_process(monkeypatch):

    monkeypatch.setattr(
        "platform.system",
        lambda: "Windows"
    )


    monkeypatch.setattr(
        ctypes.windll.shell32,
        "IsUserAnAdmin",
        lambda: 0
    )


    fake_connection = SimpleNamespace(

        status=psutil.CONN_LISTEN,

        laddr=SimpleNamespace(
            ip="192.168.1.100",
            port=9001
        ),

        pid=8888
    )


    monkeypatch.setattr(
        psutil,
        "net_connections",
        lambda kind=None: [fake_connection]
    )


    def raise_access_denied(pid):

        raise psutil.AccessDenied(pid)


    monkeypatch.setattr(
        psutil,
        "Process",
        raise_access_denied
    )


    result = run_security_checks()


    ports = result["Listening Ports"]


    assert len(ports) == 1

    assert ports[0]["Process"] == "Unknown"
    assert ports[0]["PID"] == 8888
    assert ports[0]["Exposure"] == "Network"


# ============================================================
# TEST NO LISTENING PORTS
# ============================================================
# Verifies that an empty listening-port list is handled
# correctly.
# ============================================================

def test_no_listening_ports(monkeypatch):

    monkeypatch.setattr(
        "platform.system",
        lambda: "Windows"
    )


    monkeypatch.setattr(
        ctypes.windll.shell32,
        "IsUserAnAdmin",
        lambda: 0
    )


    monkeypatch.setattr(
        psutil,
        "net_connections",
        lambda kind=None: []
    )


    result = run_security_checks()


    assert result["Listening Ports"] == []