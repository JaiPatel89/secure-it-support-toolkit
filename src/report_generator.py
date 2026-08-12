from datetime import datetime
import os


# ============================================================
# FORMAT REPORT VALUE
# ============================================================
# This function handles individual values before they are
# written to the report.
#
# It adds special formatting where required, such as adding
# a percentage sign to disk usage values.
# ============================================================

def format_value(key, value):

    if key == "Usage":
        return f"{value} %"

    else:
        return str(value)


# ============================================================
# WRITE REPORT DATA
# ============================================================
# This function recursively processes dictionaries and lists.
#
# A recursive function is useful here because the diagnostic
# data can contain several levels of nested dictionaries/lists.
#
# For example:
#
# System Health
#     └── Disk Health
#           └── List
#                 └── Dictionary
#
# This allows the report generator to handle existing modules
# as well as future modules without needing separate formatting
# code for every possible structure.
# ============================================================

def write_report_data(report, information, level=0):

    # --------------------------------------------------------
    # Dictionary
    # --------------------------------------------------------
    # Dictionaries are used by several modules to store
    # labelled information such as:
    #
    # "Firewall": "Active"
    # "Overall System Health": "Warning"
    # --------------------------------------------------------

    if isinstance(information, dict):

        for key, value in information.items():

            # ------------------------------------------------
            # Nested dictionary or list
            # ------------------------------------------------
            # If the value contains another structure, write
            # the section heading and process the contents
            # recursively.
            # ------------------------------------------------

            if isinstance(value, (dict, list)):

                report.write(f"{key}:\n")

                if isinstance(value, dict):
                    report.write("-" * len(key) + "\n")

                write_report_data(
                    report,
                    value,
                    level + 1
                )

                report.write("\n")

            # ------------------------------------------------
            # Normal dictionary value
            # ------------------------------------------------
            # Handles simple key/value information.
            # ------------------------------------------------

            else:

                formatted_value = format_value(key, value)

                report.write(
                    f"{key}: {formatted_value}\n"
                )


    # ========================================================
    # LIST
    # ========================================================
    # Lists are used by modules such as Disk Usage and
    # Process Monitor.
    #
    # Each item in the list is processed individually.
    # ========================================================

    elif isinstance(information, list):

        for item in information:

            # ------------------------------------------------
            # List containing dictionaries
            # ------------------------------------------------
            # For example:
            #
            # [
            #     {
            #         "Mount Point": "C:",
            #         "Usage": 46.5
            #     }
            # ]
            # ------------------------------------------------

            if isinstance(item, dict):

                write_report_data(
                    report,
                    item,
                    level + 1
                )

                report.write("\n")

            # ------------------------------------------------
            # List containing normal values
            # ------------------------------------------------

            else:

                report.write(f"{item}\n")


    # ========================================================
    # NORMAL VALUE
    # ========================================================
    # Handles strings, numbers and other simple values.
    # ========================================================

    else:

        report.write(f"{information}\n")


# ============================================================
# GENERATE REPORT
# ============================================================
# This is the main report-generation function.
#
# It:
#
# 1. Creates the reports directory if necessary.
# 2. Creates a timestamped filename.
# 3. Writes the report header.
# 4. Writes each diagnostic section.
# 5. Writes the report footer.
# ============================================================

def generate_report(report_data):

    # --------------------------------------------------------
    # Create reports directory
    # --------------------------------------------------------
    # If the reports folder doesn't exist, create it.
    # --------------------------------------------------------

    if not os.path.exists("reports"):
        os.makedirs("reports")


    # --------------------------------------------------------
    # Create timestamp
    # --------------------------------------------------------
    # This prevents reports from overwriting each other.
    # --------------------------------------------------------

    timestamp = datetime.now().strftime(
        "%d-%m-%Y_%H-%M-%S"
    )


    # --------------------------------------------------------
    # Create report filename
    # --------------------------------------------------------

    filename = f"reports/diagnostic_report_{timestamp}.txt"


    # --------------------------------------------------------
    # Open report file
    # --------------------------------------------------------

    with open(filename, "w") as report:

        # ====================================================
        # REPORT HEADER
        # ====================================================

        report.write("=" * 50 + "\n")
        report.write(
            "             SECURE IT SUPPORT TOOLKIT\n"
        )
        report.write(
            "                  SYSTEM REPORT\n"
        )
        report.write("=" * 50 + "\n\n")


        # ----------------------------------------------------
        # Generated timestamp
        # ----------------------------------------------------

        report.write(
            f"Generated: "
            f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}\n\n"
        )


        # ====================================================
        # REPORT SECTIONS
        # ====================================================
        # Each item in report_data represents a diagnostic
        # module that has been run by the user.
        #
        # Examples:
        #
        # System Information
        # Network Information
        # Firewall Status
        # Disk Usage
        # System Health
        # ====================================================

        for section, information in report_data.items():

            report.write("\n")
            report.write("=" * 50 + "\n")
            report.write(f"{section.upper()}\n")
            report.write("=" * 50 + "\n\n")


            # ------------------------------------------------
            # Write the section's diagnostic information.
            # ------------------------------------------------

            write_report_data(
                report,
                information
            )


        # ====================================================
        # REPORT FOOTER
        # ====================================================

        report.write("\n")
        report.write("=" * 50 + "\n")
        report.write(
            "      GENERATED BY SECURE IT SUPPORT TOOLKIT\n"
        )
        report.write("=" * 50 + "\n")