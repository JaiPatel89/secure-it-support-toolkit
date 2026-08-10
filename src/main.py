from firewall_status import get_firewall_status
from system_info import get_system_information
from network_tools import get_network_information
from disk_usage import get_disk_usage
from process_monitor import get_processes
from network_diagnostics import run_network_diagnostics
from security_checks import run_security_checks
from report_generator import generate_report



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
    print("8. Export Diagnostic Report")
    print("9. Exit")


choice = ""

while choice != "9":

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

        if not report_data:

            print("No diagnostic information available.")
            print("Please run at least one diagnostic option first.")

        else:

            generate_report(report_data)

            print("Diagnostic report generated successfully.")
    

    elif choice == "9":
        print("Exiting the program...")
        exit()
        
    else:
        print("Invalid choice. Please choose 1, 2, 3, 4, 5, 6, 7 or 8.")
        