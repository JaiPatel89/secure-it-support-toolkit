from firewall_status import get_firewall_status
from system_info import get_system_information
from network_tools import get_network_information


def display_menu():
    print("========================================")
    print("             TechAssist                 ")
    print("========================================")

    print("1. System Information")
    print("2. Network Information")
    print("3. Firewall Status")
    print("4. Exit")


choice = ""

while choice != "4":

    display_menu()

    choice = input("Choose an option: ")

    if choice == "1":
        information = get_system_information()

        for item, value in information.items():
            print(f"{item}: {value}")

    elif choice == "2":
        information = get_network_information()
        
        for adapter, details in information.items():
            
            print(f"Adapter: {adapter}")

            for detail_name, detail_value in details.items():
                print(f"{detail_name}: {detail_value}")

    elif choice == "3":
        information = get_firewall_status()

        for item, value in information.items():
            print(f"{item}: {value}")
            
    
    elif choice == "4":
        print("Exiting the program...")
        exit()
        
    else:
        print("Invalid choice. Please choose 1, 2 or 3.")
        
        