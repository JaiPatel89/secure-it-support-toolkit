# ============================================================
# REPORT GENERATOR TESTS
# ============================================================
# This module contains automated tests for report_generator.py.
#
# The tests verify that the report generator correctly:
#
# - Formats normal values
# - Adds percentage formatting to Usage values
# - Processes dictionaries
# - Processes lists
# - Processes nested dictionaries and lists
# - Creates a report file
# - Includes the generated timestamp
# - Includes diagnostic sections
# - Returns the generated report filename
#
# Temporary directories are used for file-generation tests so
# the real reports directory is not affected by the tests.
# ============================================================


# ============================================================
# TEST MODULE PATH
# ============================================================
# The application modules are stored inside the src directory.
#
# Pytest runs from the project root, so src must be added to
# Python's module search path.
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
# Import the report-generation functions being tested.
# ============================================================

from report_generator import (
    format_value,
    write_report_data,
    generate_report
)


# ============================================================
# TEST FORMAT VALUE - USAGE
# ============================================================
# Verifies that Usage values receive a percentage sign.
#
# Example:
#
#     46.5
#
# becomes:
#
#     46.5 %
# ============================================================

def test_format_value_usage():

    result = format_value(
        "Usage",
        46.5
    )

    assert result == "46.5 %"


# ============================================================
# TEST FORMAT VALUE - NORMAL VALUE
# ============================================================
# Verifies that normal values are converted to strings without
# additional formatting.
# ============================================================

def test_format_value_normal_value():

    result = format_value(
        "Status",
        "Healthy"
    )

    assert result == "Healthy"


# ============================================================
# TEST WRITE REPORT DATA - DICTIONARY
# ============================================================
# Verifies that dictionary information is correctly written
# to the report.
# ============================================================

def test_write_report_data_dictionary():

    information = {
        "Status": "Healthy",
        "Hostname": "Test-PC"
    }


    from io import StringIO

    report = StringIO()


    write_report_data(
        report,
        information
    )


    output = report.getvalue()


    assert "Status: Healthy" in output
    assert "Hostname: Test-PC" in output


# ============================================================
# TEST WRITE REPORT DATA - LIST
# ============================================================
# Verifies that lists containing dictionaries are correctly
# processed.
# ============================================================

def test_write_report_data_list():

    information = [

        {
            "Mount Point": "C:",
            "Usage": 46.5,
            "Status": "Healthy"
        }

    ]


    from io import StringIO

    report = StringIO()


    write_report_data(
        report,
        information
    )


    output = report.getvalue()


    assert "Mount Point: C:" in output
    assert "Usage: 46.5 %" in output
    assert "Status: Healthy" in output


# ============================================================
# TEST WRITE REPORT DATA - NESTED DATA
# ============================================================
# Verifies that nested dictionaries and lists are handled
# correctly.
#
# This is particularly important for System Health because it
# contains multiple levels of nested information.
# ============================================================

def test_write_report_data_nested():

    information = {

        "Disk Health": [

            {
                "Mount Point": "C:",
                "Usage": 46.5,
                "Status": "Healthy"
            }

        ],

        "Firewall Health": {

            "Domain": "Healthy",
            "Private": "Healthy",
            "Public": "Healthy"

        },

        "Overall System Health": "Warning"

    }


    from io import StringIO

    report = StringIO()


    write_report_data(
        report,
        information
    )


    output = report.getvalue()


    assert "Disk Health:" in output
    assert "Mount Point: C:" in output
    assert "Usage: 46.5 %" in output

    assert "Firewall Health:" in output
    assert "Domain: Healthy" in output
    assert "Private: Healthy" in output
    assert "Public: Healthy" in output

    assert "Overall System Health: Warning" in output


# ============================================================
# TEST GENERATE REPORT
# ============================================================
# Verifies that generate_report():
#
# - Creates the report
# - Returns a filename
# - Creates the file
# - Writes the expected report contents
#
# tmp_path is provided by pytest and gives the test a temporary
# directory that is automatically cleaned up afterwards.
# ============================================================

def test_generate_report(
    tmp_path,
    monkeypatch
):

    # --------------------------------------------------------
    # Change the working directory to pytest's temporary
    # directory.
    #
    # This prevents the test from creating files inside the
    # real project reports directory.
    # --------------------------------------------------------

    monkeypatch.chdir(
        tmp_path
    )


    report_data = {

        "System Information": {

            "Operating System": "Windows",
            "Hostname": "Test-PC"

        },

        "Disk Usage": [

            {

                "Mount Point": "C:",
                "Usage": 46.5,
                "Status": "Healthy"

            }

        ]

    }


    # --------------------------------------------------------
    # Generate the report.
    # --------------------------------------------------------

    filename = generate_report(
        report_data
    )


    # --------------------------------------------------------
    # Verify that a filename was returned.
    # --------------------------------------------------------

    assert filename is not None


    # --------------------------------------------------------
    # Convert the returned filename into a Path object.
    # --------------------------------------------------------

    report_path = Path(
        filename
    )


    # --------------------------------------------------------
    # Verify that the report file exists.
    # --------------------------------------------------------

    assert report_path.exists()


    # --------------------------------------------------------
    # Read the generated report.
    # --------------------------------------------------------

    report_contents = report_path.read_text(
        encoding="utf-8"
    )


    # --------------------------------------------------------
    # Verify the report header.
    # --------------------------------------------------------

    assert (
        "TECHASSIST"
        in report_contents
    )

    assert (
        "DIAGNOSTIC REPORT"
        in report_contents
    )

    assert (
        "Version: 1.0.0"
        in report_contents
    )


    # --------------------------------------------------------
    # Verify the timestamp is present.
    # --------------------------------------------------------

    assert (
        "Generated:"
        in report_contents
    )


    # --------------------------------------------------------
    # Verify diagnostic sections.
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
    # Verify diagnostic information.
    # --------------------------------------------------------

    assert (
        "Operating System: Windows"
        in report_contents
    )

    assert (
        "Hostname: Test-PC"
        in report_contents
    )


    # --------------------------------------------------------
    # Verify the important percentage formatting.
    # --------------------------------------------------------

    assert (
        "Usage: 46.5 %"
        in report_contents
    )


    # --------------------------------------------------------
    # Verify the report footer.
    # --------------------------------------------------------

    assert (
        "GENERATED BY TECHASSIST"
        in report_contents
    )