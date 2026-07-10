from system_info import get_system_information


def display_menu():
    print("========================================")
    print("             TechAssist                 ")
    print("========================================")

    print("1. System Information")
    print("2. Exit")


display_menu()

choice = ""

while choice != "2":

    display_menu()

    choice = input("Choose an option: ")

    if choice == "1":
        information = get_system_information()

        for item, value in information.items():
            print(f"{item}: {value}")