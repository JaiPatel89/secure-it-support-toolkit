# ============================================================
# NETWORK TOOLS TESTS
# ============================================================
# This module contains automated tests for network_tools.py.
#
# The tests verify that the network information module correctly:
#
# - Detects IPv4 addresses
# - Detects MAC addresses
# - Handles multiple network adapters
# - Ignores the localhost address
# - Ignores automatic link-local addresses
# - Excludes adapters without a usable IPv4 address
#
# Mock network adapter data is used so the tests do not depend
# on the computer's actual network configuration.
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
import psutil

from types import SimpleNamespace

from network_tools import get_network_information


# ============================================================
# TEST BASIC NETWORK INFORMATION
# ============================================================
# Verifies that an adapter containing a valid IPv4 address
# and MAC address is correctly returned.
# ============================================================

def test_network_information(monkeypatch):

    fake_addresses = {

        "Wi-Fi": [

            SimpleNamespace(
                family=socket.AF_INET,
                address="192.168.1.100"
            ),

            SimpleNamespace(
                family=psutil.AF_LINK,
                address="AA-BB-CC-DD-EE-FF"
            )

        ]

    }


    monkeypatch.setattr(
        psutil,
        "net_if_addrs",
        lambda: fake_addresses
    )


    result = get_network_information()


    assert "Wi-Fi" in result

    assert (
        result["Wi-Fi"]["IP Address"]
        == "192.168.1.100"
    )

    assert (
        result["Wi-Fi"]["MAC Address"]
        == "AA-BB-CC-DD-EE-FF"
    )


# ============================================================
# TEST MULTIPLE ADAPTERS
# ============================================================
# Verifies that multiple adapters are processed correctly.
# ============================================================

def test_multiple_adapters(monkeypatch):

    fake_addresses = {

        "Wi-Fi": [

            SimpleNamespace(
                family=socket.AF_INET,
                address="192.168.1.100"
            ),

            SimpleNamespace(
                family=psutil.AF_LINK,
                address="AA-BB-CC-DD-EE-FF"
            )

        ],

        "Ethernet": [

            SimpleNamespace(
                family=socket.AF_INET,
                address="192.168.1.101"
            ),

            SimpleNamespace(
                family=psutil.AF_LINK,
                address="11-22-33-44-55-66"
            )

        ]

    }


    monkeypatch.setattr(
        psutil,
        "net_if_addrs",
        lambda: fake_addresses
    )


    result = get_network_information()


    assert len(result) == 2

    assert (
        result["Wi-Fi"]["IP Address"]
        == "192.168.1.100"
    )

    assert (
        result["Ethernet"]["IP Address"]
        == "192.168.1.101"
    )


# ============================================================
# TEST LOCALHOST IS IGNORED
# ============================================================
# The application should ignore 127.0.0.1 because this is the
# localhost address and does not represent a usable network
# interface address.
# ============================================================

def test_localhost_is_ignored(monkeypatch):

    fake_addresses = {

        "Loopback": [

            SimpleNamespace(
                family=socket.AF_INET,
                address="127.0.0.1"
            ),

            SimpleNamespace(
                family=psutil.AF_LINK,
                address="00-00-00-00-00-00"
            )

        ]

    }


    monkeypatch.setattr(
        psutil,
        "net_if_addrs",
        lambda: fake_addresses
    )


    result = get_network_information()


    assert result == {}


# ============================================================
# TEST LINK-LOCAL ADDRESS IS IGNORED
# ============================================================
# Addresses beginning with 169.254 are automatically assigned
# when a device cannot obtain an address from DHCP.
#
# The application deliberately ignores these addresses.
# ============================================================

def test_link_local_address_is_ignored(monkeypatch):

    fake_addresses = {

        "Wi-Fi": [

            SimpleNamespace(
                family=socket.AF_INET,
                address="169.254.10.20"
            ),

            SimpleNamespace(
                family=psutil.AF_LINK,
                address="AA-BB-CC-DD-EE-FF"
            )

        ]

    }


    monkeypatch.setattr(
        psutil,
        "net_if_addrs",
        lambda: fake_addresses
    )


    result = get_network_information()


    assert result == {}


# ============================================================
# TEST ADAPTER WITHOUT IPV4 ADDRESS
# ============================================================
# An adapter containing only a MAC address should not be
# included because the function requires a usable IPv4 address.
# ============================================================

def test_adapter_without_ipv4(monkeypatch):

    fake_addresses = {

        "Ethernet": [

            SimpleNamespace(
                family=psutil.AF_LINK,
                address="AA-BB-CC-DD-EE-FF"
            )

        ]

    }


    monkeypatch.setattr(
        psutil,
        "net_if_addrs",
        lambda: fake_addresses
    )


    result = get_network_information()


    assert result == {}


# ============================================================
# TEST NON-IP ADDRESSES ARE IGNORED
# ============================================================
# Verifies that IPv6 and other address families do not
# interfere with IPv4 detection.
# ============================================================

def test_non_ipv4_addresses_are_ignored(monkeypatch):

    fake_addresses = {

        "Wi-Fi": [

            SimpleNamespace(
                family=socket.AF_INET6,
                address="fe80::1234"
            ),

            SimpleNamespace(
                family=socket.AF_INET,
                address="192.168.1.100"
            ),

            SimpleNamespace(
                family=psutil.AF_LINK,
                address="AA-BB-CC-DD-EE-FF"
            )

        ]

    }


    monkeypatch.setattr(
        psutil,
        "net_if_addrs",
        lambda: fake_addresses
    )


    result = get_network_information()


    assert (
        result["Wi-Fi"]["IP Address"]
        == "192.168.1.100"
    )

    assert (
        result["Wi-Fi"]["MAC Address"]
        == "AA-BB-CC-DD-EE-FF"
    )