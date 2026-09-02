# ============================================================
# TECHASSIST MAIN APPLICATION
# ============================================================
# This is the main entry point for the Secure IT Support
# Toolkit.
#
# The main application provides an interactive menu that allows
# the user to run individual diagnostic modules.
#
# Available options:
#
# 1. System Information
# 2. Network Information
# 3. Firewall Status
# 4. Disk Usage
# 5. Process Monitor
# 6. Network Diagnostics
# 7. Security Checks
# 8. Service Status
# 9. System Health
# 10. Export Diagnostic Report
# 11. Exit
#
# Each diagnostic module performs a specific task and returns
# information to this main program.
#
# The information is stored in report_data so that the user can
# run several diagnostics and then export all collected results
# into a single diagnostic report.
#
# Option 9 combines several diagnostic modules to provide an
# overall assessment of the system.
#
# Option 10 passes the collected information to
# report_generator.py.
#
# Error handling is included around individual diagnostic
# operations so that a problem with one module does not
# unnecessarily terminate the entire application.
# ============================================================


# ============================================================
# MODULE IMPORTS
# ============================================================
# Each imported function provides a specific diagnostic
# capability.
#
# firewall_status:
#     Checks the operating-system firewall.
#
# system_info:
#     Collects general system information.
#
# network_tools:
#     Collects network adapter information.
#
# disk_usage:
#     Checks available disk space.
#
# process_monitor:
#     Identifies the top processes by memory usage.
#
# network_diagnostics:
#     Tests connectivity, DNS, latency and gateway information.
#
# security_checks:
#     Checks privileges and listening network ports.
#
# service_status:
#     Checks important operating-system services.
#
# report_generator:
#     Creates the final diagnostic report.
#
# system_health:
#     Evaluates the results of several diagnostic modules and
#     calculates the overall system health.
# ============================================================

import sys

from firewall_status import get_firewall_status
from system_info import get_system_information
from network_tools import get_network_information
from disk_usage import get_disk_usage
from process_monitor import get_processes
from network_diagnostics import run_network_diagnostics
from security_checks import run_security_checks
from service_status import get_service_status
from report_generator import generate_report


from system_health import (
    check_disk_health,
    check_firewall_health,
    check_security_health,
    check_service_health,
    calculate_overall_health
)


# ============================================================
# APPLICATION INFORMATION
# ============================================================

APP_NAME = "TechAssist"
APP_VERSION = "1.0.0"

if len(sys.argv) > 1 and sys.argv[1] == "--version":
    print(f"{APP_NAME} version {APP_VERSION}")
    sys.exit(0)

# ============================================================
# REPORT DATA
# ============================================================
# Stores diagnostic results collected during the current
# TechAssist session.
#
# Each diagnostic option adds its results to this dictionary.
#
# The dictionary is later passed to report_generator.py when
# the user selects option 10.
# ============================================================

report_data = {}


# ============================================================
# DISPLAY MENU
# ============================================================
# Displays the main TechAssist menu.
#
# Keeping the menu in its own function makes the main program
# easier to read and allows the menu to be changed without
# modifying the diagnostic logic.
# ============================================================

def display_menu():

    print(
        "========================================"
    )

    print(
        f"             {APP_NAME}"
    )

    print(
        f"          Version {APP_VERSION}"
    )

    print(
        "========================================"
    )

    print(
        "1. System Information"
    )

    print(
        "2. Network Information"
    )

    print(
        "3. Firewall Status"
    )

    print(
        "4. Disk Usage"
    )

    print(
        "5. Process Monitor"
    )

    print(
        "6. Network Diagnostics"
    )

    print(
        "7. Security Checks"
    )

    print(
        "8. Service Status"
    )

    print(
        "9. System Health"
    )

    print(
        "10. Export Diagnostic Report"
    )

    print(
        "11. Exit"
    )


# ============================================================
# MAIN APPLICATION LOOP
# ============================================================
# The menu continues to appear until the user selects option
# 11.
# ============================================================

choice = ""


while choice != "11":

    # --------------------------------------------------------
    # Display the menu.
    # --------------------------------------------------------

    display_menu()


    # --------------------------------------------------------
    # Request the user's choice.
    # --------------------------------------------------------

    choice = input(
        "Choose an option: "
    )


    # ========================================================
    # OPTION 1 - SYSTEM INFORMATION
    # ========================================================
    # Collects information about the computer's operating
    # system, processor, memory and storage.
    # ========================================================

    if choice == "1":

        try:

            information = get_system_information()


            report_data[
                "System Information"
            ] = information


            for item, value in information.items():

                print(
                    f"{item}: {value}"
                )


        except Exception as error:

            print(
                f"Unable to retrieve system information: "
                f"{error}"
            )


    # ========================================================
    # OPTION 2 - NETWORK INFORMATION
    # ========================================================
    # Displays the network adapters detected by the toolkit,
    # along with their IP and MAC addresses.
    # ========================================================

    elif choice == "2":

        try:

            information = get_network_information()


            report_data[
                "Network Information"
            ] = information


            for adapter, details in information.items():

                print(
                    f"Adapter: {adapter}"
                )


                for detail_name, detail_value in details.items():

                    print(
                        f"{detail_name}: "
                        f"{detail_value}"
                    )


        except Exception as error:

            print(
                f"Unable to retrieve network information: "
                f"{error}"
            )


    # ========================================================
    # OPTION 3 - FIREWALL STATUS
    # ========================================================
    # Retrieves the status of the operating-system firewall.
    #
    # Windows reports individual profiles:
    #
    #     Domain
    #     Private
    #     Public
    #
    # Linux/macOS report the firewall as Active or Inactive.
    # ========================================================

    elif choice == "3":

        try:

            information = get_firewall_status()


            report_data[
                "Firewall Status"
            ] = information


            for item, value in information.items():

                print(
                    f"{item}: {value}"
                )


        except Exception as error:

            print(
                f"Unable to retrieve firewall status: "
                f"{error}"
            )


    # ========================================================
    # OPTION 4 - DISK USAGE
    # ========================================================
    # Displays storage information for detected drives.
    #
    # Usage is displayed with a percentage sign.
    # ========================================================

    elif choice == "4":

        try:

            information = get_disk_usage()


            report_data[
                "Disk Usage"
            ] = information


            print()
            print(
                "Disk Usage Information:"
            )

            print(
                "----------------------"
            )


            for index, drive in enumerate(
                information,
                start=1
            ):

                print()
                print(
                    f"Drive {index}:"
                )

                print(
                    "----------"
                )


                for key, value in drive.items():

                    if key == "Usage":

                        print(
                            f"{key}: "
                            f"{value} %"
                        )

                    else:

                        print(
                            f"{key}: "
                            f"{value}"
                        )


        except Exception as error:

            print(
                f"Unable to retrieve disk usage: "
                f"{error}"
            )


    # ========================================================
    # OPTION 5 - PROCESS MONITOR
    # ========================================================
    # Displays the top ten processes based on memory usage.
    #
    # The process monitor also provides:
    #
    # - Process name
    # - PID
    # - Status
    # - CPU usage
    # - Memory usage
    # ========================================================

    elif choice == "5":

        try:

            information = get_processes()


            report_data[
                "Process Monitor"
            ] = information


            print()
            print(
                "Top 10 Processes by Memory Usage:"
            )

            print(
                "----------------------------------"
            )


            for index, process in enumerate(
                information,
                start=1
            ):

                print()
                print(
                    f"Process {index}:"
                )

                print(
                    "-------------"
                )


                for key, value in process.items():

                    print(
                        f"{key}: {value}"
                    )


        except Exception as error:

            print(
                f"Unable to retrieve process information: "
                f"{error}"
            )


    # ========================================================
    # OPTION 6 - NETWORK DIAGNOSTICS
    # ========================================================
    # Performs active network tests including:
    #
    # - Internet connectivity
    # - Ping latency
    # - Packet loss
    # - DNS resolution
    # - Local IP address
    # - Default gateway
    # ========================================================

    elif choice == "6":

        try:

            information = run_network_diagnostics()


            report_data[
                "Network Diagnostics"
            ] = information


            print()
            print(
                "Network Diagnostics:"
            )

            print(
                "-------------------------"
            )


            for item, value in information.items():

                print(
                    f"{item}: {value}"
                )


        except Exception as error:

            print(
                f"Unable to run network diagnostics: "
                f"{error}"
            )


    # ========================================================
    # OPTION 7 - SECURITY CHECKS
    # ========================================================
    # Performs security-related checks including:
    #
    # - Administrator/Root privileges
    # - Listening network ports
    # - Processes associated with listening ports
    # - Network exposure
    # ========================================================

    elif choice == "7":

        try:

            information = run_security_checks()


            report_data[
                "Security Checks"
            ] = information


            for key, value in information.items():


                # ------------------------------------------------
                # Listening ports are returned as a list of
                # dictionaries.
                # ------------------------------------------------

                if isinstance(
                    value,
                    list
                ):

                    print()
                    print(
                        f"{key}:"
                    )

                    print(
                        "-" * 40
                    )


                    for item in value:

                        if isinstance(
                            item,
                            dict
                        ):

                            for item_key, item_value in item.items():

                                print(
                                    f"{item_key}: "
                                    f"{item_value}"
                                )

                            print()


                else:

                    print(
                        f"{key}: {value}"
                    )


        except Exception as error:

            print(
                f"Unable to perform security checks: "
                f"{error}"
            )


    # ========================================================
    # OPTION 8 - SERVICE STATUS
    # ========================================================
    # Checks important operating-system services.
    #
    # The service module returns both the operating system and
    # the individual service statuses.
    # ========================================================

    elif choice == "8":

        try:

            results = get_service_status()


            report_data[
                "Service Status"
            ] = results


            print()
            print(
                f"Operating System: "
                f"{results['Operating System']}"
            )


            for service, status in results[
                "Services"
            ].items():

                print(
                    f"{service}: {status}"
                )


        except Exception as error:

            print(
                f"Unable to retrieve service status: "
                f"{error}"
            )


    # ========================================================
    # OPTION 9 - SYSTEM HEALTH
    # ========================================================
    # Runs several diagnostic modules and evaluates their
    # results.
    #
    # The health checks include:
    #
    # - Disk Health
    # - Firewall Health
    # - Security Health
    # - Service Health
    #
    # These are then combined into:
    #
    # Overall System Health
    #
    # Possible overall results:
    #
    #     Healthy
    #     Warning
    #     Critical
    # ========================================================

    elif choice == "9":

        try:

            # ------------------------------------------------
            # DISK HEALTH
            # ------------------------------------------------

            disk_information = get_disk_usage()

            disk_results = check_disk_health(
                disk_information
            )


            # ------------------------------------------------
            # FIREWALL HEALTH
            # ------------------------------------------------

            firewall_information = get_firewall_status()

            firewall_results = check_firewall_health(
                firewall_information
            )


            # ------------------------------------------------
            # SECURITY HEALTH
            # ------------------------------------------------

            security_information = run_security_checks()

            security_results = check_security_health(
                security_information
            )


            # ------------------------------------------------
            # SERVICE HEALTH
            # ------------------------------------------------

            service_information = get_service_status()

            service_results = check_service_health(
                service_information
            )


            # ------------------------------------------------
            # CALCULATE OVERALL HEALTH
            # ------------------------------------------------

            overall_status = calculate_overall_health(

                disk_results,

                firewall_results,

                security_results,

                service_results

            )


            # ------------------------------------------------
            # STORE HEALTH INFORMATION
            # ------------------------------------------------

            health_information = {

                "Disk Health":
                    disk_results,

                "Firewall Health":
                    firewall_results,

                "Security Health":
                    security_results,

                "Service Health":
                    service_results,

                "Overall System Health":
                    overall_status

            }


            report_data[
                "System Health"
            ] = health_information


            # =================================================
            # DISPLAY SYSTEM HEALTH
            # =================================================

            print()
            print(
                "SYSTEM HEALTH"
            )

            print(
                "-------------"
            )


            # ------------------------------------------------
            # Display Disk Health
            # ------------------------------------------------

            print()
            print(
                "Disk Health:"
            )


            for drive in disk_results:

                print(
                    f"Mount Point: "
                    f"{drive['Mount Point']}"
                )

                print(
                    f"Usage: "
                    f"{drive['Usage']} %"
                )

                print(
                    f"Status: "
                    f"{drive['Status']}"
                )

                print()


            # ------------------------------------------------
            # Display Firewall Health
            # ------------------------------------------------

            print(
                "Firewall Health:"
            )


            for profile, status in firewall_results.items():

                print(
                    f"{profile}: {status}"
                )


            # ------------------------------------------------
            # Display Security Health
            # ------------------------------------------------

            print()
            print(
                "Security Health:"
            )


            for check, status in security_results.items():

                print(
                    f"{check}: {status}"
                )


            # ------------------------------------------------
            # Display Service Health
            # ------------------------------------------------

            print()
            print(
                "Service Health:"
            )


            for service, status in service_results.items():

                print(
                    f"{service}: {status}"
                )


            # ------------------------------------------------
            # Display Overall Health
            # ------------------------------------------------

            print()
            print(
                "Overall System Health:"
            )

            print(
                f"Status: "
                f"{overall_status}"
            )


        except Exception as error:

            print(
                f"Unable to calculate system health: "
                f"{error}"
            )


    # ========================================================
    # OPTION 10 - EXPORT DIAGNOSTIC REPORT
    # ========================================================
    # Generates a text report containing all diagnostic
    # information collected during the current session.
    #
    # At least one diagnostic option must be run before a report
    # can be generated.
    # ========================================================

    elif choice == "10":

        if not report_data:

            print()
            print(
                "No diagnostic information available."
            )

            print(
                "Please run at least one diagnostic "
                "option first."
            )


        else:

            try:

                report_filename = generate_report(
                    report_data
                )


                if report_filename:

                    print()
                    print(
                        "Diagnostic report generated "
                        "successfully."
                    )

                    print(
                        f"Report: "
                        f"{report_filename}"
                    )

                else:

                    print(
                        "Diagnostic report could not "
                        "be generated."
                    )


            except Exception as error:

                print(
                    f"Unable to generate diagnostic report: "
                    f"{error}"
                )


    # ========================================================
    # OPTION 11 - EXIT
    # ========================================================
    # Ends the TechAssist application.
    # ========================================================

    elif choice == "11":

        print(
            "Exiting the program..."
        )

        break


    # ========================================================
    # INVALID MENU OPTION
    # ========================================================
    # Handles input that does not correspond to one of the
    # available menu options.
    # ========================================================

    else:

        print()
        print(
            "Invalid choice. "
            "Please choose an option from 1 to 11."
        )