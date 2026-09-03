# ============================================================
# MAIN APPLICATION TESTS
# ============================================================
# This test module verifies the behaviour of the TechAssist
# main application.
#
# The tests run main.py as a separate process because the main
# application contains an interactive menu that starts when the
# file is executed.
#
# Running the application as a subprocess allows the tests to:
#
# - Provide menu selections automatically
# - Verify menu output
# - Test the exit option
# - Test invalid input
# - Test individual diagnostic options
# - Test report generation
#
# These tests complement the unit tests for the individual
# diagnostic modules by testing how the modules work together
# through the main application.
# ============================================================


# ============================================================
# MODULE IMPORTS
# ============================================================
# subprocess:
#     Runs main.py as a separate Python process.
#
# sys:
#     Provides the Python executable used to run the tests.
#
# os:
#     Provides file and directory handling for report tests.
#
# pathlib:
#     Provides a convenient way to locate the project files.
# ============================================================

import subprocess
import sys
import os
from pathlib import Path


# ============================================================
# MAIN.PY LOCATION
# ============================================================
# Determine the project root directory from this test file.
#
# The test file is located inside:
#
#     tests/
#
# Therefore the parent directory is the project root.
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

MAIN_FILE = PROJECT_ROOT / "src" / "main.py"


# ============================================================
# RUN MAIN APPLICATION
# ============================================================
# This helper function runs main.py and provides menu choices
# to the application.
#
# Input is supplied through stdin.
#
# The function returns the completed subprocess so individual
# tests can inspect the output and return code.
# ============================================================

def run_main(user_input):

    result = subprocess.run(

        [
            sys.executable,
            str(MAIN_FILE)
        ],

        input=user_input,

        capture_output=True,

        text=True,

        cwd=PROJECT_ROOT,

        timeout=30
    )

    return result


# ============================================================
# TEST MENU DISPLAY
# ============================================================
# Verifies that the main application displays the expected
# menu options.
# ============================================================

def test_main_menu():

    result = run_main(
        "11\n"
    )


    # --------------------------------------------------------
    # Verify the application completed successfully.
    # --------------------------------------------------------

    assert result.returncode == 0


    # --------------------------------------------------------
    # Verify the main menu is displayed.
    # --------------------------------------------------------

    assert "TechAssist" in result.stdout


    # --------------------------------------------------------
    # Verify the available menu options.
    # --------------------------------------------------------

    assert "1. System Information" in result.stdout

    assert "2. Network Information" in result.stdout

    assert "3. Firewall Status" in result.stdout

    assert "4. Disk Usage" in result.stdout

    assert "5. Process Monitor" in result.stdout

    assert "6. Network Diagnostics" in result.stdout

    assert "7. Security Checks" in result.stdout

    assert "8. Service Status" in result.stdout

    assert "9. System Health" in result.stdout

    assert "10. Export Diagnostic Report" in result.stdout

    assert "11. Exit" in result.stdout


def test_version_command():
    result = subprocess.run(
        [sys.executable, "src/main.py", "--version"],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert result.stdout.strip() == "TechAssist version 1.0.0"


def test_help_command():
    result = subprocess.run(
        [sys.executable, "src/main.py", "--help"],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert "TechAssist - IT Support Diagnostic Toolkit" in result.stdout
    assert "python src/main.py --version" in result.stdout
    assert "python src/main.py --help" in result.stdout    


# ============================================================
# TEST APPLICATION VERSION
# ============================================================
# Verifies that the TechAssist application displays its
# current version when the main menu is shown.
# ============================================================

def test_application_version():

    result = run_main(
        "11\n"
    )


    assert result.returncode == 0


    assert (
        "Version 1.0.0"
        in result.stdout
    )


# ============================================================
# TEST EXIT OPTION
# ============================================================
# Verifies that selecting option 11 exits the application
# correctly.
# ============================================================

def test_exit_option():

    result = run_main(
        "11\n"
    )


    assert result.returncode == 0


    assert (
        "Exiting the program..."
        in result.stdout
    )


# ============================================================
# TEST INVALID MENU OPTION
# ============================================================
# Verifies that an invalid menu selection does not terminate
# the application unexpectedly.
#
# The application should display an error message and then
# continue until option 11 is selected.
# ============================================================

def test_invalid_menu_option():

    result = run_main(
        "99\n"
        "11\n"
    )


    assert result.returncode == 0


    assert (
        "Invalid choice."
        in result.stdout
    )


# ============================================================
# TEST SYSTEM INFORMATION
# ============================================================
# Verifies that option 1 successfully launches the system
# information module.
# ============================================================

def test_system_information_option():

    result = run_main(
        "1\n"
        "11\n"
    )


    assert result.returncode == 0


    # --------------------------------------------------------
    # The output should contain information produced by the
    # system information module.
    # --------------------------------------------------------

    assert "Operating System" in result.stdout

    assert "Hostname" in result.stdout

    assert "Architecture" in result.stdout


# ============================================================
# TEST NETWORK INFORMATION
# ============================================================
# Verifies that option 2 successfully launches the network
# information module.
# ============================================================

def test_network_information_option():

    result = run_main(
        "2\n"
        "11\n"
    )


    assert result.returncode == 0


    assert (
        "Adapter:"
        in result.stdout
    )


# ============================================================
# TEST FIREWALL STATUS
# ============================================================
# Verifies that option 3 successfully launches the firewall
# status module.
# ============================================================

def test_firewall_status_option():

    result = run_main(
        "3\n"
        "11\n"
    )


    assert result.returncode == 0


    # --------------------------------------------------------
    # Firewall output varies by operating system, so verify
    # that the module produced output rather than checking a
    # specific firewall profile.
    # --------------------------------------------------------

    assert (
        "Firewall"
        in result.stdout
        or
        "firewall"
        in result.stdout
        or
        "Domain"
        in result.stdout
        or
        "Private"
        in result.stdout
        or
        "Public"
        in result.stdout
    )


# ============================================================
# TEST DISK USAGE
# ============================================================
# Verifies that option 4 successfully launches the disk usage
# module.
# ============================================================

def test_disk_usage_option():

    result = run_main(
        "4\n"
        "11\n"
    )


    assert result.returncode == 0


    assert (
        "Disk Usage Information:"
        in result.stdout
    )


# ============================================================
# TEST PROCESS MONITOR
# ============================================================
# Verifies that option 5 successfully launches the process
# monitor.
# ============================================================

def test_process_monitor_option():

    result = run_main(
        "5\n"
        "11\n"
    )


    assert result.returncode == 0


    assert (
        "Top 10 Processes by Memory Usage:"
        in result.stdout
    )


# ============================================================
# TEST NETWORK DIAGNOSTICS
# ============================================================
# Verifies that option 6 successfully launches the network
# diagnostics module.
# ============================================================

def test_network_diagnostics_option():

    result = run_main(
        "6\n"
        "11\n"
    )


    assert result.returncode == 0


    assert (
        "Network Diagnostics:"
        in result.stdout
    )


# ============================================================
# TEST SECURITY CHECKS
# ============================================================
# Verifies that option 7 successfully launches the security
# checks module.
# ============================================================

def test_security_checks_option():

    result = run_main(
        "7\n"
        "11\n"
    )


    assert result.returncode == 0


    # --------------------------------------------------------
    # The security module can produce different information
    # depending on the operating system.
    # --------------------------------------------------------

    assert (
        "Administrator Privileges"
        in result.stdout

        or

        "Root Privileges"
        in result.stdout

        or

        "Listening Ports"
        in result.stdout
    )


# ============================================================
# TEST SERVICE STATUS
# ============================================================
# Verifies that option 8 successfully launches the service
# status module.
# ============================================================

def test_service_status_option():

    result = run_main(
        "8\n"
        "11\n"
    )


    assert result.returncode == 0


    assert (
        "Operating System:"
        in result.stdout
    )


# ============================================================
# TEST SYSTEM HEALTH
# ============================================================
# Verifies that option 9 successfully combines the diagnostic
# modules and produces an overall health result.
# ============================================================

def test_system_health_option():

    result = run_main(
        "9\n"
        "11\n"
    )


    assert result.returncode == 0


    assert (
        "SYSTEM HEALTH"
        in result.stdout
    )


    assert (
        "Overall System Health:"
        in result.stdout
    )


# ============================================================
# TEST REPORT WITHOUT DIAGNOSTICS
# ============================================================
# Verifies that option 10 correctly refuses to generate a
# report when no diagnostic information has been collected.
# ============================================================

def test_report_without_diagnostics():

    result = run_main(
        "10\n"
        "11\n"
    )


    assert result.returncode == 0


    assert (
        "No diagnostic information available."
        in result.stdout
    )


# ============================================================
# TEST REPORT GENERATION
# ============================================================
# Verifies that the application can:
#
# 1. Run a diagnostic.
# 2. Store the result in report_data.
# 3. Export the collected information.
#
# A report file should be created in the reports directory.
# ============================================================

def test_report_generation():

    reports_directory = (
        PROJECT_ROOT / "reports"
    )


    # --------------------------------------------------------
    # Record existing reports before the test.
    # --------------------------------------------------------

    existing_reports = set(
        reports_directory.glob(
            "diagnostic_report_*.txt"
        )
    )


    # --------------------------------------------------------
    # Run system information followed by report generation.
    # --------------------------------------------------------

    result = run_main(
        "1\n"
        "10\n"
        "11\n"
    )


    assert result.returncode == 0


    assert (
        "Diagnostic report generated successfully."
        in result.stdout
    )


    # --------------------------------------------------------
    # Find newly created reports.
    # --------------------------------------------------------

    current_reports = set(
        reports_directory.glob(
            "diagnostic_report_*.txt"
        )
    )


    new_reports = (
        current_reports
        - existing_reports
    )


    assert len(new_reports) >= 1


    # --------------------------------------------------------
    # Verify the generated report contains the expected
    # diagnostic section.
    # --------------------------------------------------------

    newest_report = max(
        new_reports,
        key=os.path.getmtime
    )


    with open(
        newest_report,
        "r",
        encoding="utf-8"
    ) as report:

        report_contents = report.read()


    assert (
        "SYSTEM INFORMATION"
        in report_contents
    )


    # --------------------------------------------------------
    # Clean up the report created by this test.
    # --------------------------------------------------------

    newest_report.unlink()


# ============================================================
# TEST MULTIPLE DIAGNOSTICS
# ============================================================
# Verifies that the application can collect more than one
# diagnostic result before generating a report.
#
# This tests the central report_data dictionary and confirms
# that information from multiple modules can be retained.
# ============================================================

def test_multiple_diagnostics():

    reports_directory = (
        PROJECT_ROOT / "reports"
    )


    existing_reports = set(
        reports_directory.glob(
            "diagnostic_report_*.txt"
        )
    )


    # --------------------------------------------------------
    # Run two diagnostics followed by report generation.
    # --------------------------------------------------------

    result = run_main(
        "1\n"
        "4\n"
        "10\n"
        "11\n"
    )


    assert result.returncode == 0


    assert (
        "Diagnostic report generated successfully."
        in result.stdout
    )


    # --------------------------------------------------------
    # Locate the newly generated report.
    # --------------------------------------------------------

    current_reports = set(
        reports_directory.glob(
            "diagnostic_report_*.txt"
        )
    )


    new_reports = (
        current_reports
        - existing_reports
    )


    assert len(new_reports) >= 1


    newest_report = max(
        new_reports,
        key=os.path.getmtime
    )


    with open(
        newest_report,
        "r",
        encoding="utf-8"
    ) as report:

        report_contents = report.read()


    # --------------------------------------------------------
    # Verify both diagnostic sections were retained.
    # --------------------------------------------------------

    assert (
        "SYSTEM INFORMATION"
        in report_contents
    )


    assert (
        "DISK USAGE"
        in report_contents
    )


    # --------------------------------------------------------
    # Clean up the generated report.
    # --------------------------------------------------------

    newest_report.unlink()