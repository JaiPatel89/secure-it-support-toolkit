# ============================================================
# REPORT GENERATOR MODULE
# ============================================================
# This module creates a text-based diagnostic report containing
# information collected by the TechAssist diagnostic modules.
#
# The report can contain information from:
#
# - System Information
# - Network Information
# - Firewall Status
# - Disk Usage
# - Process Monitor
# - Network Diagnostics
# - Security Checks
# - Service Status
# - System Health
#
# The module uses a recursive function to process dictionaries
# and lists of different depths.
#
# This is important because some diagnostic modules return
# simple dictionaries while others return nested structures.
#
# For example:
#
# System Health
#     └── Disk Health
#           └── List
#                 └── Dictionary
#
# The report generator can process this structure without
# requiring separate formatting code for every module.
#
# Reports are stored in the "reports" directory.
#
# Each report receives a timestamped filename so that previous
# reports are not overwritten.
#
# Error handling is included around file operations so that
# problems creating or writing a report are handled cleanly.
# ============================================================


# ============================================================
# MODULE IMPORTS
# ============================================================
# datetime:
#     Used to generate timestamps for the report and filename.
#
# os:
#     Used to create and check the reports directory.
# ============================================================

from datetime import datetime
import os


APP_NAME = "TechAssist"
APP_VERSION = "1.0.0"


# ============================================================
# FORMAT REPORT VALUE
# ============================================================
# Formats individual values before they are written to the
# report.
#
# Disk usage is stored internally as a number, for example:
#
#     46.5
#
# The report should display this as:
#
#     46.5 %
#
# Other values are converted to strings normally.
# ============================================================

def format_value(key, value):

    if key == "Usage":

        return f"{value} %"

    else:

        return str(value)


# ============================================================
# WRITE REPORT DATA
# ============================================================
# Recursively processes dictionaries and lists and writes their
# contents to the report.
#
# A recursive function calls itself when it encounters another
# dictionary or list.
#
# This allows the same function to handle structures such as:
#
# Dictionary
#     └── Dictionary
#
# Dictionary
#     └── List
#           └── Dictionary
#
# This approach makes the report generator easier to maintain
# when new diagnostic modules are added in the future.
# ============================================================

def write_report_data(
    report,
    information,
    level=0
):


    # ========================================================
    # DICTIONARY
    # ========================================================
    # Dictionaries contain labelled information.
    #
    # Examples:
    #
    # "Firewall": "Active"
    #
    # "Overall System Health": "Warning"
    # ========================================================

    if isinstance(
        information,
        dict
    ):

        for key, value in information.items():


            # ------------------------------------------------
            # NESTED DICTIONARY OR LIST
            # ------------------------------------------------
            # If a value contains another dictionary or list,
            # write the key as a heading and recursively process
            # the contents.
            # ------------------------------------------------

            if isinstance(
                value,
                (dict, list)
            ):

                report.write(
                    f"{key}:\n"
                )


                # ------------------------------------------------
                # Add an underline for dictionary sections.
                # ------------------------------------------------

                if isinstance(
                    value,
                    dict
                ):

                    report.write(
                        "-" * len(key)
                        + "\n"
                    )


                write_report_data(
                    report,
                    value,
                    level + 1
                )


                report.write(
                    "\n"
                )


            # ------------------------------------------------
            # NORMAL DICTIONARY VALUE
            # ------------------------------------------------
            # Handles simple key/value information.
            # ------------------------------------------------

            else:

                formatted_value = format_value(
                    key,
                    value
                )


                report.write(
                    f"{key}: "
                    f"{formatted_value}\n"
                )


    # ========================================================
    # LIST
    # ========================================================
    # Lists are used by modules such as:
    #
    # - Disk Usage
    # - Process Monitor
    # - Listening Ports
    #
    # Each item in the list is processed individually.
    # ========================================================

    elif isinstance(
        information,
        list
    ):

        for item in information:


            # ------------------------------------------------
            # LIST CONTAINING A DICTIONARY
            # ------------------------------------------------
            # Example:
            #
            # [
            #     {
            #         "Mount Point": "C:",
            #         "Usage": 46.5,
            #         "Status": "Healthy"
            #     }
            # ]
            # ------------------------------------------------

            if isinstance(
                item,
                dict
            ):

                write_report_data(
                    report,
                    item,
                    level + 1
                )


                report.write(
                    "\n"
                )


            # ------------------------------------------------
            # LIST CONTAINING A NORMAL VALUE
            # ------------------------------------------------

            else:

                report.write(
                    f"{item}\n"
                )


    # ========================================================
    # NORMAL VALUE
    # ========================================================
    # Handles strings, numbers and other simple values.
    # ========================================================

    else:

        report.write(
            f"{information}\n"
        )


# ============================================================
# GENERATE REPORT
# ============================================================
# This is the main report-generation function.
#
# It:
#
# 1. Creates the reports directory.
# 2. Generates a timestamp.
# 3. Creates a unique report filename.
# 4. Opens the report file.
# 5. Writes the report header.
# 6. Writes each diagnostic section.
# 7. Writes the report footer.
#
# The function returns the filename when successful.
#
# Returning the filename makes it possible for main.py or a
# future version of TechAssist to tell the user exactly where
# the report was created.
# ============================================================

def generate_report(report_data):


    # ========================================================
    # CREATE REPORTS DIRECTORY
    # ========================================================
    # If the reports directory does not exist, create it.
    # exist_ok=True prevents an error if the directory already
    # exists.
    # ========================================================

    try:

        os.makedirs(
            "reports",
            exist_ok=True
        )


    except OSError as error:

        print(
            f"Unable to create reports directory: "
            f"{error}"
        )

        return None


    # ========================================================
    # CREATE TIMESTAMP
    # ========================================================
    # The timestamp ensures that each report has a unique
    # filename.
    #
    # Example:
    #
    # 14-08-2026_13-30-45
    # ========================================================

    timestamp = datetime.now().strftime(
        "%d-%m-%Y_%H-%M-%S"
    )


    # ========================================================
    # CREATE REPORT FILENAME
    # ========================================================

    filename = (
        f"reports/"
        f"diagnostic_report_"
        f"{timestamp}.txt"
    )


    # ========================================================
    # OPEN REPORT FILE
    # ========================================================
    # UTF-8 encoding allows the report to safely contain a wide
    # range of characters.
    # ========================================================

    try:

        with open(
            filename,
            "w",
            encoding="utf-8"
        ) as report:


            # =================================================
            # REPORT HEADER
            # =================================================

            report.write(
                "=" * 50
                + "\n"
            )

            report.write(
                f"             {APP_NAME.upper()}\n"
            )

            report.write(
                "             DIAGNOSTIC REPORT\n"
            )

            report.write(
                f"             Version: {APP_VERSION}\n"
            )

            report.write(
                "=" * 50
                + "\n\n"
            )


            # =================================================
            # GENERATED TIMESTAMP
            # =================================================

            report.write(
                f"Generated: "
                f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
                f"\n\n"
            )


            # =================================================
            # REPORT SECTIONS
            # =================================================
            # Each item in report_data represents a diagnostic
            # section that has been run by the user.
            #
            # Examples:
            #
            # System Information
            # Network Information
            # Firewall Status
            # System Health
            # =================================================

            for section, information in report_data.items():

                report.write(
                    "\n"
                )

                report.write(
                    "=" * 50
                    + "\n"
                )

                report.write(
                    f"{section.upper()}\n"
                )

                report.write(
                    "=" * 50
                    + "\n\n"
                )


                # ------------------------------------------------
                # Write diagnostic information.
                # ------------------------------------------------

                write_report_data(
                    report,
                    information
                )


            # =================================================
            # REPORT FOOTER
            # =================================================

            report.write(
                "\n"
            )

            report.write(
                "=" * 50
                + "\n"
            )

            report.write(
                f"              GENERATED BY {APP_NAME.upper()}\n"
            )

            report.write(
                "=" * 50
                + "\n"
            )


    # ========================================================
    # FILE WRITING ERROR
    # ========================================================

    except OSError as error:

        print(
            f"Unable to generate report: "
            f"{error}"
        )

        return None


    # ========================================================
    # SUCCESS
    # ========================================================
    # Return the generated filename.
    # ========================================================

    return filename


# ============================================================
# STANDALONE TEST
# ============================================================
# This section allows report_generator.py to be tested
# independently from main.py.
#
# A small sample report is generated to confirm that:
#
# - The reports directory can be created.
# - The report file can be written.
# - Dictionaries are processed.
# - Lists are processed.
# - Nested structures are processed.
# - Percentage formatting works.
# ============================================================

if __name__ == "__main__":

    test_report_data = {

        "System Information": {

            "Operating System": "Windows",

            "Architecture": "64-bit"

        },


        "Disk Usage": [

            {

                "Mount Point": "C:",

                "Usage": 46.5,

                "Status": "Healthy"

            }

        ],


        "System Health": {

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

    }


    print(
        "Generating test diagnostic report..."
    )


    report_filename = generate_report(
        test_report_data
    )


    if report_filename:

        print(
            "Diagnostic report generated successfully."
        )

        print(
            f"Report: {report_filename}"
        )

    else:

        print(
            "Diagnostic report could not be generated."
        )