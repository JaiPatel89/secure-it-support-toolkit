# ============================================================
# REPORT GENERATOR MODULE
# ============================================================
# This module creates a text-based diagnostic report from the
# information collected by the Secure IT Support Toolkit.
#
# The report generator is responsible for:
#
# - Creating the reports directory
# - Creating a unique timestamped report filename
# - Writing the report header
# - Formatting diagnostic information
# - Handling nested dictionaries and lists
# - Writing each diagnostic section
# - Writing the report footer
#
# The module is designed to work with the data structures
# returned by the other toolkit modules without needing
# separate report-writing code for each module.
# ============================================================


# ============================================================
# MODULE IMPORTS
# ============================================================

# datetime is used to generate timestamps for the report
# filename and report contents.
from datetime import datetime


# os provides functions for working with directories and files.
import os


# ============================================================
# FORMAT REPORT VALUE
# ============================================================
# Handles individual values before they are written to the
# report.
#
# Some values require additional formatting.
#
# For example:
#
# Usage: 46.5
#
# becomes:
#
# Usage: 46.5 %
#
# Keeping this formatting in a separate function means the
# report-writing logic does not need to contain special cases
# throughout the module.
# ============================================================

def format_value(key, value):

    # Disk usage is stored internally as a numeric value so that
    # system_health.py can perform calculations against it.
    #
    # The percentage symbol is added only when generating the
    # human-readable report.
    if key == "Usage":

        return f"{value} %"


    # All other values are converted to strings without
    # additional formatting.
    else:

        return str(value)


# ============================================================
# WRITE REPORT DATA
# ============================================================
# Recursively processes diagnostic information and writes it
# into the report.
#
# The diagnostic modules do not all return the same data
# structure.
#
# Some return:
#
# - Dictionaries
# - Lists
# - Lists containing dictionaries
# - Dictionaries containing lists
# - Nested dictionaries
#
# A recursive function allows the report generator to process
# all of these structures using the same logic.
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
    #
    # "Operating System": "Windows"
    # ========================================================

    if isinstance(information, dict):


        # Process every key/value pair in the dictionary.
        for key, value in information.items():


            # =================================================
            # NESTED DICTIONARY OR LIST
            # =================================================
            # If a value contains another dictionary or list,
            # write the key as a heading and recursively process
            # its contents.
            #
            # This allows complex structures such as System
            # Health to be written without hard-coding the
            # structure of each module.
            # =================================================

            if isinstance(
                value,
                (dict, list)
            ):

                # Write the section heading.
                report.write(
                    f"{key}:\n"
                )


                # Add an underline when the nested structure
                # is a dictionary.
                if isinstance(value, dict):

                    report.write(
                        "-" * len(key) + "\n"
                    )


                # Process the nested structure.
                write_report_data(
                    report,
                    value,
                    level + 1
                )


                # Add spacing after the nested section.
                report.write("\n")


            # =================================================
            # NORMAL DICTIONARY VALUE
            # =================================================
            # Handles simple key/value pairs such as:
            #
            # "Hostname": "DESKTOP-PC"
            #
            # "Status": "Healthy"
            # =================================================

            else:

                # Apply any required formatting.
                formatted_value = format_value(
                    key,
                    value
                )


                # Write the formatted key/value pair.
                report.write(
                    f"{key}: {formatted_value}\n"
                )


    # ========================================================
    # LIST
    # ========================================================
    # Lists are used by modules that can return multiple items.
    #
    # Examples:
    #
    # - Multiple disk partitions
    # - Multiple processes
    # - Multiple listening ports
    # ========================================================

    elif isinstance(
        information,
        list
    ):


        # Process each item in the list.
        for item in information:


            # =================================================
            # LIST CONTAINING DICTIONARIES
            # =================================================
            # This is common for disk information, process
            # information and listening-port information.
            # =================================================

            if isinstance(
                item,
                dict
            ):

                # Recursively process the dictionary.
                write_report_data(
                    report,
                    item,
                    level + 1
                )


                # Add spacing between individual items.
                report.write("\n")


            # =================================================
            # LIST CONTAINING NORMAL VALUES
            # =================================================
            # Handles lists containing simple strings or
            # numbers.
            # =================================================

            else:

                report.write(
                    f"{item}\n"
                )


    # ========================================================
    # NORMAL VALUE
    # ========================================================
    # Handles simple values such as strings and numbers.
    # ========================================================

    else:

        report.write(
            f"{information}\n"
        )


# ============================================================
# GENERATE REPORT
# ============================================================
# Main report-generation function.
#
# This function:
#
# 1. Creates the reports directory if required.
# 2. Creates a timestamp for the report.
# 3. Creates a unique report filename.
# 4. Opens the report file.
# 5. Writes the report header.
# 6. Writes each diagnostic section.
# 7. Writes the report footer.
# ============================================================

def generate_report(report_data):


    # ========================================================
    # CREATE REPORTS DIRECTORY
    # ========================================================
    # The toolkit stores generated reports inside a dedicated
    # "reports" directory.
    #
    # If the directory already exists, nothing needs to be done.
    # ========================================================

    if not os.path.exists("reports"):

        os.makedirs("reports")


    # ========================================================
    # CREATE TIMESTAMP
    # ========================================================
    # The timestamp is used to make each report filename
    # unique.
    #
    # Example:
    #
    # diagnostic_report_12-08-2026_13-57-58.txt
    #
    # This prevents new reports from overwriting previous
    # reports.
    # ========================================================

    timestamp = datetime.now().strftime(
        "%d-%m-%Y_%H-%M-%S"
    )


    # ========================================================
    # CREATE REPORT FILENAME
    # ========================================================

    filename = (
        f"reports/"
        f"diagnostic_report_{timestamp}.txt"
    )


    # ========================================================
    # OPEN REPORT FILE
    # ========================================================
    # "w" opens the file for writing.
    #
    # The file is automatically closed when the with block
    # finishes.
    # ========================================================

    with open(
        filename,
        "w"
    ) as report:


        # ====================================================
        # REPORT HEADER
        # ====================================================
        # Provides a consistent title at the beginning of
        # every diagnostic report.
        # ====================================================

        report.write(
            "=" * 50 + "\n"
        )

        report.write(
            "             SECURE IT SUPPORT TOOLKIT\n"
        )

        report.write(
            "                  SYSTEM REPORT\n"
        )

        report.write(
            "=" * 50 + "\n\n"
        )


        # ====================================================
        # GENERATED TIMESTAMP
        # ====================================================
        # Records exactly when the diagnostic report was
        # generated.
        # ====================================================

        report.write(
            f"Generated: "
            f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}\n\n"
        )


        # ====================================================
        # REPORT SECTIONS
        # ====================================================
        # report_data contains the diagnostic sections collected
        # by main.py.
        #
        # Only modules that the user has actually run are added
        # to report_data.
        #
        # This means the report can contain:
        #
        # System Information
        # Network Information
        # Firewall Status
        # Disk Usage
        # Process Monitor
        # Network Diagnostics
        # Security Checks
        # Service Status
        # System Health
        #
        # depending on which options the user selected.
        # ====================================================

        for section, information in report_data.items():


            # ------------------------------------------------
            # SECTION HEADER
            # ------------------------------------------------
            # Each section receives a consistent visual header.
            # ------------------------------------------------

            report.write(
                "\n"
            )

            report.write(
                "=" * 50 + "\n"
            )

            report.write(
                f"{section.upper()}\n"
            )

            report.write(
                "=" * 50 + "\n\n"
            )


            # ------------------------------------------------
            # WRITE SECTION DATA
            # ------------------------------------------------
            # Pass the section's data to the recursive writer.
            # ------------------------------------------------

            write_report_data(
                report,
                information
            )


        # ====================================================
        # REPORT FOOTER
        # ====================================================
        # Marks the end of the generated diagnostic report.
        # ====================================================

        report.write(
            "\n"
        )

        report.write(
            "=" * 50 + "\n"
        )

        report.write(
            "      GENERATED BY SECURE IT SUPPORT TOOLKIT\n"
        )

        report.write(
            "=" * 50 + "\n"
        )