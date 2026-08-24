# ============================================================
# NETWORK DIAGNOSTICS TESTS
# ============================================================
# This module contains automated tests for
# network_diagnostics.py.
#
# The tests verify that the network diagnostics module can:
#
# - Detect internet connectivity
# - Extract ping latency
# - Extract packet loss
# - Detect DNS resolution
# - Detect the local IP address
# - Detect the default gateway
# - Handle failed internet connectivity
#
# External commands such as ping and ipconfig are mocked.
# This prevents the tests from depending on the actual network
# connection of the computer running the tests.
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

import socket
import subprocess

import psutil

from types import SimpleNamespace

from network_diagnostics import run_network_diagnostics


# ============================================================
# TEST WINDOWS NETWORK DIAGNOSTICS
# ============================================================
# Verifies that the Windows version correctly processes:
#
# - Internet connectivity
# - Ping latency
# - Packet loss
# - DNS resolution
# - Local IP address
# - Default gateway
# ============================================================

def test_windows_network_diagnostics(monkeypatch):

    # --------------------------------------------------------
    # Pretend that the operating system is Windows.
    # --------------------------------------------------------

    monkeypatch.setattr(
        "platform.system",
        lambda: "Windows"
    )


    # --------------------------------------------------------
    # Create fake ping output.
    # --------------------------------------------------------

    ping_output = """
Pinging 8.8.8.8 with 32 bytes of data:
Reply from 8.8.8.8: bytes=32 time=20ms TTL=117

Ping statistics for 8.8.8.8:
    Packets: Sent = 1, Received = 1, Lost = 0 (0% loss),
Approximate round trip times in milli-seconds:
    Minimum = 20ms, Maximum = 20ms, Average = 20ms
"""


    # --------------------------------------------------------
    # Create fake ipconfig output.
    # --------------------------------------------------------

    ipconfig_output = """
Windows IP Configuration

Wireless LAN adapter Wi-Fi:

   IPv4 Address. . . . . . . . . . . : 192.168.1.100
   Default Gateway . . . . . . . . . : 192.168.1.1
"""


    # --------------------------------------------------------
    # Mock subprocess.run().
    #
    # The command being executed determines which fake output
    # should be returned.
    # --------------------------------------------------------

    def fake_run(
        command,
        capture_output=True,
        text=True,
        timeout=None
    ):  

        if command[0] == "ping":

            return SimpleNamespace(
                returncode=0,
                stdout=ping_output,
                stderr=""
            )


        if command[0] == "ipconfig":

            return SimpleNamespace(
                returncode=0,
                stdout=ipconfig_output,
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


    # --------------------------------------------------------
    # Mock DNS resolution.
    # --------------------------------------------------------

    monkeypatch.setattr(
        socket,
        "gethostbyname",
        lambda hostname: "142.250.187.196"
    )


    # --------------------------------------------------------
    # Mock network interface information.
    # --------------------------------------------------------

    fake_addresses = {

        "Wi-Fi": [

            SimpleNamespace(
                family=socket.AF_INET,
                address="192.168.1.100"
            )

        ]

    }


    monkeypatch.setattr(
        psutil,
        "net_if_addrs",
        lambda: fake_addresses
    )


    # --------------------------------------------------------
    # Run diagnostics.
    # --------------------------------------------------------

    result = run_network_diagnostics()


    # --------------------------------------------------------
    # Verify internet connectivity.
    # --------------------------------------------------------

    assert (
        result["Internet Connectivity"]
        == "Connected"
    )


    # --------------------------------------------------------
    # Verify ping latency.
    # --------------------------------------------------------

    assert (
        result["Ping Latency"]
        == "20ms"
    )


    # --------------------------------------------------------
    # Verify packet loss.
    # --------------------------------------------------------

    assert (
        result["Packet Loss"]
        == "0% loss"
    )


    # --------------------------------------------------------
    # Verify DNS resolution.
    # --------------------------------------------------------

    assert (
        result["DNS Resolution"]
        == "Working"
    )


    # --------------------------------------------------------
    # Verify local IP address.
    # --------------------------------------------------------

    assert (
        result["Local IP Address"]
        == "192.168.1.100"
    )


    # --------------------------------------------------------
    # Verify default gateway.
    # --------------------------------------------------------

    assert (
        result["Default Gateway"]
        == "192.168.1.1"
    )


# ============================================================
# TEST FAILED INTERNET CONNECTION
# ============================================================
# Verifies that a failed ping is correctly reported as
# disconnected.
# ============================================================

def test_internet_disconnected(monkeypatch):

    monkeypatch.setattr(
        "platform.system",
        lambda: "Windows"
    )


    # --------------------------------------------------------
    # Mock ping failure.
    # --------------------------------------------------------

    def fake_run(
        command,
        capture_output=True,
        text=True,
        timeout=None
   ):

        return SimpleNamespace(
            returncode=1,
            stdout="",
            stderr="Request timed out."
        )


    monkeypatch.setattr(
        subprocess,
        "run",
        fake_run
    )


    # --------------------------------------------------------
    # DNS still works in this test.
    # --------------------------------------------------------

    monkeypatch.setattr(
        socket,
        "gethostbyname",
        lambda hostname: "142.250.187.196"
    )


    # --------------------------------------------------------
    # Provide a local IP address.
    # --------------------------------------------------------

    fake_addresses = {

        "Wi-Fi": [

            SimpleNamespace(
                family=socket.AF_INET,
                address="192.168.1.100"
            )

        ]

    }


    monkeypatch.setattr(
        psutil,
        "net_if_addrs",
        lambda: fake_addresses
    )


    result = run_network_diagnostics()


    assert (
        result["Internet Connectivity"]
        == "Disconnected"
    )


# ============================================================
# TEST DNS FAILURE
# ============================================================
# Verifies that a DNS lookup failure is correctly detected.
# ============================================================

def test_dns_resolution_failure(monkeypatch):

    monkeypatch.setattr(
        "platform.system",
        lambda: "Windows"
    )


    # --------------------------------------------------------
    # Make ping fail.
    # --------------------------------------------------------

    monkeypatch.setattr(
        subprocess,
        "run",
        lambda command, capture_output=True, text=True:
            SimpleNamespace(
                returncode=1,
                stdout="",
                stderr=""
            )
    )


    # --------------------------------------------------------
    # Make DNS resolution fail.
    # --------------------------------------------------------

    def dns_failure(hostname):

        raise socket.gaierror(
            "DNS resolution failed"
        )


    monkeypatch.setattr(
        socket,
        "gethostbyname",
        dns_failure
    )


    # --------------------------------------------------------
    # Provide a local IP address.
    # --------------------------------------------------------

    fake_addresses = {

        "Wi-Fi": [

            SimpleNamespace(
                family=socket.AF_INET,
                address="192.168.1.100"
            )

        ]

    }


    monkeypatch.setattr(
        psutil,
        "net_if_addrs",
        lambda: fake_addresses
    )


    result = run_network_diagnostics()


    assert (
        result["DNS Resolution"]
        == "Failed"
    )


# ============================================================
# TEST LOCALHOST IS IGNORED
# ============================================================
# Verifies that 127.0.0.1 is not returned as the local IP.
# ============================================================

def test_localhost_is_ignored(monkeypatch):

    monkeypatch.setattr(
        "platform.system",
        lambda: "Windows"
    )


    # --------------------------------------------------------
    # Mock failed ping.
    # --------------------------------------------------------

    monkeypatch.setattr(
        subprocess,
        "run",
        lambda command, capture_output=True, text=True:
            SimpleNamespace(
                returncode=1,
                stdout="",
                stderr=""
            )
    )


    monkeypatch.setattr(
        socket,
        "gethostbyname",
        lambda hostname: "142.250.187.196"
    )


    # --------------------------------------------------------
    # Only localhost is available.
    # --------------------------------------------------------

    fake_addresses = {

        "Loopback": [

            SimpleNamespace(
                family=socket.AF_INET,
                address="127.0.0.1"
            )

        ]

    }


    monkeypatch.setattr(
        psutil,
        "net_if_addrs",
        lambda: fake_addresses
    )


    result = run_network_diagnostics()


    # --------------------------------------------------------
    # No local IP should be reported.
    # --------------------------------------------------------

    assert (
        "Local IP Address"
        not in result
    )


# ============================================================
# TEST LINK-LOCAL ADDRESS IS IGNORED
# ============================================================
# Verifies that a 169.254.x.x address is not treated as a
# usable local IP address.
# ============================================================

def test_link_local_address_is_ignored(monkeypatch):

    monkeypatch.setattr(
        "platform.system",
        lambda: "Windows"
    )


    monkeypatch.setattr(
        subprocess,
        "run",
        lambda command, capture_output=True, text=True:
            SimpleNamespace(
                returncode=1,
                stdout="",
                stderr=""
            )
    )


    monkeypatch.setattr(
        socket,
        "gethostbyname",
        lambda hostname: "142.250.187.196"
    )


    fake_addresses = {

        "Wi-Fi": [

            SimpleNamespace(
                family=socket.AF_INET,
                address="169.254.10.20"
            )

        ]

    }


    monkeypatch.setattr(
        psutil,
        "net_if_addrs",
        lambda: fake_addresses
    )


    result = run_network_diagnostics()


    assert (
        "Local IP Address"
        not in result
    )