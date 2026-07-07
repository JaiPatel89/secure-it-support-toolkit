from system_info import get_system_information


print("========================================")
print(" Secure IT Support Toolkit")
print(" System Information Report")
print("========================================")

information = get_system_information()


for item, value in information.items():
    print(f"{item}: {value}")