# ============================================================
# MODULE IMPORTS
# ============================================================
# Import the functions provided by each diagnostic module.
#
# Each module is responsible for collecting or analysing one
# specific area of the computer system. Keeping these functions
# in separate modules makes the project easier to maintain and
# allows individual components to be tested independently.
# ============================================================

from firewall_status import get_firewall_status
from system_info import get_system_information
from network_tools import get_network_information
from disk_usage import get_disk_usage
from process_monitor import get_processes
from network_diagnostics import run_network_diagnostics
from security_checks import run_security_checks
from service_status import get_service_status
from report_generator import generate_report


# System Health imports
#
# These functions take information collected by the existing
# diagnostic modules and assess whether each area is Healthy,
# Warning or Critical.
from system_health import (
    check_disk_health,
    check_firewall_health,
    check_security_health,
    check_service_health,
    calculate_overall_health
)


# ============================================================
# REPORT DATA STORAGE
# ============================================================
# This dictionary stores the results of diagnostic checks
# selected by the user.
#
# The information is retained while the program is running so
# that the user can run several diagnostics and then export all
# collected results as a single report.
# ============================================================

report_data = {}


# ============================================================
# DISPLAY MENU
# ============================================================
# Displays the main menu and the diagnostic options available
# to the user.
#
# The menu acts as the central interface for the toolkit.
# ============================================================

def display_menu():

    print("========================================")
    print("             TechAssist                 ")
    print("========================================")

    print("1. System Information")
    print("2. Network Information")
    print("3. Firewall Status")
    print("4. Disk Usage")
    print("5. Process Monitor")
    print("6. Network Diagnostics")
    print("7. Security Checks")
    print("8. Service Status")
    print("9. System Health")
    print("10. Export Diagnostic Report")
    print("11. Exit")


# ============================================================
# MAIN PROGRAM LOOP
# ============================================================
# The program continues displaying the menu until the user
# selects option 11.
#
# The user's menu selection is stored in 'choice' and used to
# determine which diagnostic function should be executed.
# ============================================================

choice = ""

while choice != "11":

    display_menu()

    choice = input("Choose an option: ")


    # ========================================================
    # OPTION 1 - SYSTEM INFORMATION
    # ========================================================
    # Collects basic information about the computer, including
    # operating system, hostname, processor, memory and disk
    # information.
    # ========================================================

    if choice == "1":

        information = get_system_information()

        # Store the results so they can later be included in
        # the exported diagnostic report.
        report_data["System Information"] = information

        for item, value in information.items():
            print(f"{item}: {value}")


    # ========================================================
    # OPTION 2 - NETWORK INFORMATION
    # ========================================================
    # Collects information about the system's network
    # adapters and their configuration.
    # ========================================================

    elif choice == "2":

        information = get_network_information()

        report_data["Network Information"] = information

        for adapter, details in information.items():

            print(f"Adapter: {adapter}")

            for detail_name, detail_value in details.items():
                print(f"{detail_name}: {detail_value}")


    # ========================================================
    # OPTION 3 - FIREWALL STATUS
    # ========================================================
    # Checks the status of the operating system firewall.
    #
    # The firewall module handles operating-system-specific
    # commands for Windows, Linux and macOS.
    # ========================================================

    elif choice == "3":

        information = get_firewall_status()

        report_data["Firewall Status"] = information

        for item, value in information.items():
            print(f"{item}: {value}")


    # ========================================================
    # OPTION 4 - DISK USAGE
    # ========================================================
    # Displays storage information for detected drives or
    # partitions.
    #
    # Usage is displayed with a percentage sign to make the
    # output easier for the user to understand.
    # ========================================================

    elif choice == "4":

        information = get_disk_usage()

        report_data["Disk Usage"] = information

        print("\nDisk Usage Information:")
        print("----------------------")

        for index, drive in enumerate(information, start=1):

            print(f"\nDrive {index}:")
            print("----------")

            for key, value in drive.items():

                if key == "Usage":
                    print(f"{key}: {value} %")

                else:
                    print(f"{key}: {value}")


    # ========================================================
    # OPTION 5 - PROCESS MONITOR
    # ========================================================
    # Displays the top processes identified by the process
    # monitoring module.
    #
    # The information is also stored in report_data so that
    # it can be included in the diagnostic report.
    # ========================================================

    elif choice == "5":

        information = get_processes()

        report_data["Process Monitor"] = information

        print("\nTop 10 Processes by Memory Usage:")
        print("----------------------------------")

        for index, process in enumerate(information, start=1):

            print(f"\nProcess {index}:")
            print("-------------")

            for key, value in process.items():
                print(f"{key}: {value}")


    # ========================================================
    # OPTION 6 - NETWORK DIAGNOSTICS
    # ========================================================
    # Runs network troubleshooting checks such as connectivity
    # and network configuration tests.
    # ========================================================

    elif choice == "6":

        information = run_network_diagnostics()

        report_data["Network Diagnostics"] = information

        print("\nNetwork Diagnostics:")
        print("-------------------------")

        for item, value in information.items():
            print(f"{item}: {value}")


    # ========================================================
    # OPTION 7 - SECURITY CHECKS
    # ========================================================
    # Performs security-related checks, including identifying
    # listening network ports and checking administrator/root
    # privileges.
    #
    # Listening ports are stored as a list of dictionaries, so
    # the code checks for list values and displays their
    # individual fields.
    # ========================================================

    elif choice == "7":

        information = run_security_checks()

        report_data["Security Checks"] = information

        for key, value in information.items():

            if isinstance(value, list):

                print(f"\n{key}:")
                print("-" * 40)

                for item in value:

                    for item_key, item_value in item.items():
                        print(f"{item_key}: {item_value}")

                    print()

            else:
                print(f"{key}: {value}")


    # ========================================================
    # OPTION 8 - SERVICE STATUS
    # ========================================================
    # Checks the status of selected operating-system services.
    #
    # The service_status module handles the differences between
    # Windows, Linux and macOS service-management systems.
    # ========================================================

    elif choice == "8":

        results = get_service_status()

        report_data["Service Status"] = results

        print(f"\nOperating System: {results['Operating System']}")

        for service, status in results["Services"].items():
            print(f"{service}: {status}")


    # ========================================================
    # OPTION 9 - SYSTEM HEALTH
    # ========================================================
    # System Health combines several existing diagnostic
    # modules and interprets their results.
    #
    # It assesses:
    #
    # - Disk health
    # - Firewall health
    # - Security health
    # - Service health
    #
    # These results are then combined into one overall status:
    #
    # Healthy
    # Warning
    # Critical
    #
    # The System Health feature does not collect the underlying
    # information itself. Instead, it reuses the existing
    # diagnostic modules and evaluates their results.
    # ========================================================

    elif choice == "9":

        # ----------------------------------------------------
        # Disk Health
        # ----------------------------------------------------
        # Collect disk information and pass it to the health
        # assessment function.
        # ----------------------------------------------------

        disk_information = get_disk_usage()
        disk_results = check_disk_health(disk_information)


        # ----------------------------------------------------
        # Firewall Health
        # ----------------------------------------------------
        # Collect firewall information and assess the status
        # of each firewall profile.
        # ----------------------------------------------------

        firewall_information = get_firewall_status()
        firewall_results = check_firewall_health(
            firewall_information
        )


        # ----------------------------------------------------
        # Security Health
        # ----------------------------------------------------
        # Run the existing security checks and assess their
        # results.
        # ----------------------------------------------------

        security_information = run_security_checks()
        security_results = check_security_health(
            security_information
        )


        # ----------------------------------------------------
        # Service Health
        # ----------------------------------------------------
        # Collect service status information and determine
        # whether each monitored service is healthy or requires
        # attention.
        # ----------------------------------------------------

        service_information = get_service_status()
        service_results = check_service_health(
            service_information
        )


        # ----------------------------------------------------
        # Overall System Health
        # ----------------------------------------------------
        # Combine the results from all four health categories
        # to produce a single overall system status.
        # ----------------------------------------------------

        overall_status = calculate_overall_health(
            disk_results,
            firewall_results,
            security_results,
            service_results
        )


        # ----------------------------------------------------
        # Prepare System Health Report Data
        # ----------------------------------------------------
        # Store all health information together so that the
        # report generator can include it in the exported
        # diagnostic report.
        # ----------------------------------------------------

        health_information = {
            "Disk Health": disk_results,
            "Firewall Health": firewall_results,
            "Security Health": security_results,
            "Service Health": service_results,
            "Overall System Health": overall_status
        }

        report_data["System Health"] = health_information


        # ----------------------------------------------------
        # Display System Health Results
        # ----------------------------------------------------

        print("\nSYSTEM HEALTH")
        print("-------------")


        print("\nDisk Health:")

        for drive in disk_results:

            print(f"Mount Point: {drive['Mount Point']}")
            print(f"Usage: {drive['Usage']} %")
            print(f"Status: {drive['Status']}")
            print()


        print("Firewall Health:")

        for profile, status in firewall_results.items():
            print(f"{profile}: {status}")


        print("\nSecurity Health:")

        for check, status in security_results.items():
            print(f"{check}: {status}")


        print("\nService Health:")

        for service, status in service_results.items():
            print(f"{service}: {status}")


        print("\nOverall System Health:")
        print(f"Status: {overall_status}")


    # ========================================================
    # OPTION 10 - EXPORT DIAGNOSTIC REPORT
    # ========================================================
    # Generates a text report containing all diagnostic
    # information collected during the current program session.
    #
    # A report cannot be generated if the user has not run any
    # diagnostic options.
    # ========================================================

    elif choice == "10":

        if not report_data:

            print("No diagnostic information available.")
            print("Please run at least one diagnostic option first.")

        else:

            generate_report(report_data)

            print("Diagnostic report generated successfully.")


    # ========================================================
    # OPTION 11 - EXIT
    # ========================================================
    # Ends the program when the user selects the exit option.
    # ========================================================

    elif choice == "11":

        print("Exiting the program...")
        exit()


    # ========================================================
    # INVALID MENU OPTION
    # ========================================================
    # Handles input that does not match one of the available
    # menu options.
    # ========================================================

    else:

        print("Invalid choice. Please choose an option from 1 to 11.")
        