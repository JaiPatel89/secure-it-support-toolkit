# ============================================================
# SYSTEM HEALTH TESTS
# ============================================================
# This module contains automated tests for system_health.py.
#
# The tests verify that the System Health module correctly:
#
# - Classifies disk usage
# - Classifies firewall status
# - Evaluates administrator/root privileges
# - Identifies network-exposed ports
# - Evaluates service status
# - Calculates the overall system health
#
# These tests use controlled test data rather than relying on
# the actual computer's current configuration.
#
# This makes the tests predictable and repeatable.
# ============================================================


# ============================================================
# TEST MODULE PATH
# ============================================================
# The application modules are stored inside the src directory.
#
# Pytest runs from the project root, so we add src to Python's
# module search path.
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
# MODULE IMPORT
# ============================================================
# Import the functions being tested from system_health.py.
# ============================================================

from system_health import (
    check_disk_health,
    check_firewall_health,
    check_security_health,
    check_service_health,
    calculate_overall_health
)


# ============================================================
# TEST DISK HEALTH
# ============================================================
# Verifies that disk usage below 80% is considered Healthy.
# ============================================================

def test_disk_health_healthy():

    disk_information = [
        {
            "Mount Point": "C:",
            "Usage": 46.5
        }
    ]

    result = check_disk_health(
        disk_information
    )

    assert result[0]["Status"] == "Healthy"


# ============================================================
# TEST DISK HEALTH WARNING
# ============================================================
# Verifies that disk usage of 80% or more is considered
# Warning.
# ============================================================

def test_disk_health_warning():

    disk_information = [
        {
            "Mount Point": "C:",
            "Usage": 80
        }
    ]

    result = check_disk_health(
        disk_information
    )

    assert result[0]["Status"] == "Warning"


# ============================================================
# TEST DISK HEALTH CRITICAL
# ============================================================
# Verifies that disk usage of 90% or more is considered
# Critical.
# ============================================================

def test_disk_health_critical():

    disk_information = [
        {
            "Mount Point": "C:",
            "Usage": 90
        }
    ]

    result = check_disk_health(
        disk_information
    )

    assert result[0]["Status"] == "Critical"


# ============================================================
# TEST FIREWALL HEALTH
# ============================================================
# Verifies that an active firewall is considered Healthy.
# ============================================================

def test_firewall_health():

    firewall_information = {
        "Domain": "on",
        "Private": "on",
        "Public": "on"
    }

    result = check_firewall_health(
        firewall_information
    )

    assert result["Domain"] == "Healthy"
    assert result["Private"] == "Healthy"
    assert result["Public"] == "Healthy"


# ============================================================
# TEST FIREWALL HEALTH - INACTIVE
# ============================================================
# Verifies that an inactive firewall is considered Critical.
# ============================================================

def test_firewall_health_inactive():

    firewall_information = {
        "Domain": "off"
    }

    result = check_firewall_health(
        firewall_information
    )

    assert result["Domain"] == "Critical"


# ============================================================
# TEST SECURITY HEALTH
# ============================================================
# Verifies that non-administrator users are considered
# Healthy.
#
# It also verifies that network-exposed ports generate a
# Warning.
# ============================================================

def test_security_health():

    security_information = {

        "Administrator Privileges": "No",

        "Listening Ports": [

            {
                "Address": "0.0.0.0:80",
                "Process": "TestProcess",
                "PID": 1234,
                "Exposure": "Network"
            }

        ]

    }

    result = check_security_health(
        security_information
    )

    assert (
        result["Administrator Privileges"]
        == "Healthy"
    )

    assert (
        result["Network Exposed Ports"]
        == "Warning - 1 exposed"
    )


# ============================================================
# TEST SECURITY HEALTH - NO EXPOSED PORTS
# ============================================================
# Verifies that no network-exposed ports are considered
# Healthy.
# ============================================================

def test_security_health_no_exposed_ports():

    security_information = {

        "Administrator Privileges": "No",

        "Listening Ports": [

            {
                "Address": "127.0.0.1:8884",
                "Process": "TestProcess",
                "PID": 1234,
                "Exposure": "Localhost"
            }

        ]

    }

    result = check_security_health(
        security_information
    )

    assert (
        result["Network Exposed Ports"]
        == "Healthy"
    )


# ============================================================
# TEST SERVICE HEALTH
# ============================================================
# Verifies that running services are Healthy and stopped
# services generate a Warning.
# ============================================================

def test_service_health():

    service_information = {

        "Services": {

            "Windows Update": "Running",
            "DNS Client": "Stopped"

        }

    }

    result = check_service_health(
        service_information
    )

    assert (
        result["Windows Update"]
        == "Healthy"
    )

    assert (
        result["DNS Client"]
        == "Warning"
    )


# ============================================================
# TEST OVERALL HEALTH - HEALTHY
# ============================================================
# If every section is Healthy, the overall status should also
# be Healthy.
# ============================================================

def test_overall_health_healthy():

    disk_health = [
        {
            "Mount Point": "C:",
            "Usage": 46.5,
            "Status": "Healthy"
        }
    ]

    firewall_health = {
        "Domain": "Healthy",
        "Private": "Healthy",
        "Public": "Healthy"
    }

    security_health = {
        "Administrator Privileges": "Healthy",
        "Network Exposed Ports": "Healthy"
    }

    service_health = {
        "DNS Client": "Healthy"
    }

    result = calculate_overall_health(
        disk_health,
        firewall_health,
        security_health,
        service_health
    )

    assert result == "Healthy"


# ============================================================
# TEST OVERALL HEALTH - WARNING
# ============================================================
# If at least one section has a Warning and there are no
# Critical results, the overall status should be Warning.
# ============================================================

def test_overall_health_warning():

    disk_health = [
        {
            "Mount Point": "C:",
            "Usage": 46.5,
            "Status": "Healthy"
        }
    ]

    firewall_health = {
        "Domain": "Healthy"
    }

    security_health = {
        "Administrator Privileges": "Healthy",
        "Network Exposed Ports": "Warning - 1 exposed"
    }

    service_health = {
        "DNS Client": "Healthy"
    }

    result = calculate_overall_health(
        disk_health,
        firewall_health,
        security_health,
        service_health
    )

    assert result == "Warning"


# ============================================================
# TEST OVERALL HEALTH - CRITICAL
# ============================================================
# Critical takes priority over Warning and Healthy.
# ============================================================

def test_overall_health_critical():

    disk_health = [
        {
            "Mount Point": "C:",
            "Usage": 95,
            "Status": "Critical"
        }
    ]

    firewall_health = {
        "Domain": "Healthy"
    }

    security_health = {
        "Administrator Privileges": "Healthy"
    }

    service_health = {
        "DNS Client": "Warning"
    }

    result = calculate_overall_health(
        disk_health,
        firewall_health,
        security_health,
        service_health
    )

    assert result == "Critical"