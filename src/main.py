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


report_data = {}


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


choice = ""

while choice != "11":

    display_menu()

    choice = input("Choose an option: ")

    if choice == "1":
        information = get_system_information()

        report_data["System Information"] = information

        for item, value in information.items():
            print(f"{item}: {value}")

    elif choice == "2":
        information = get_network_information()

        report_data["Network Information"] = information
        
        for adapter, details in information.items():
            
            print(f"Adapter: {adapter}")

            for detail_name, detail_value in details.items():
                print(f"{detail_name}: {detail_value}")

    elif choice == "3":
        information = get_firewall_status()

        report_data["Firewall Status"] = information

        for item, value in information.items():
            print(f"{item}: {value}")
            
    
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

    elif choice == "6":
        information = run_network_diagnostics()

        report_data["Network Diagnostics"] = information

        print("\nNetwork Diagnostics:")
        print("-------------------------")

        for item, value in information.items():
            print(f"{item}: {value}")


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


    elif choice == "8":
        results = get_service_status()

        report_data["Service Status"] = results

        print(f"\nOperating System: {results['Operating System']}")

        for service, status in results["Services"].items():
            print(f"{service}: {status}")


    elif choice == "9":

        disk_information = get_disk_usage()
        disk_results = check_disk_health(disk_information)

        firewall_information = get_firewall_status()
        firewall_results = check_firewall_health(firewall_information)

        security_information = run_security_checks()
        security_results = check_security_health(security_information)

        service_information = get_service_status()
        service_results = check_service_health(service_information)

        overall_status = calculate_overall_health(
            disk_results,
            firewall_results,
            security_results,
            service_results
        )

        health_information = {
            "Disk Health": disk_results,
            "Firewall Health": firewall_results,
            "Security Health": security_results,
            "Service Health": service_results,
            "Overall System Health": overall_status
        }

        report_data["System Health"] = health_information

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


    elif choice == "10":

        if not report_data:

            print("No diagnostic information available.")
            print("Please run at least one diagnostic option first.")

        else:

            generate_report(report_data)

            print("Diagnostic report generated successfully.")
    

    elif choice == "11":
        print("Exiting the program...")
        exit()
        
    else:
        print("Invalid choice. Please choose an option from 1 to 11.")
        