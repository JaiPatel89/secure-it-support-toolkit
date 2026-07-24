import platform
import subprocess

def get_firewall_status():

    operating_system = platform.system()

    if operating_system == "Windows":
        result = subprocess.run(
            ["netsh", "advfirewall", "show", "allprofiles"], 
            capture_output=True, 
            text=True

        )

        firewall_output = result.stdout

        firewall_status = {}
        current_profile = None

        lines = firewall_output.splitlines()

        for line in lines:
            if "Domain Profile Settings" in line:
                current_profile = "Domain"

            elif "Private Profile Settings" in line:
                current_profile = "Private"

            elif "Public Profile Settings" in line:
                current_profile = "Public"

            elif "State" in line:
                firewall_status[current_profile] = line.split()[-1]

        for profile, status in firewall_status.items():
            print(f"{profile} Firewall: {status}")



    elif operating_system == "Linux":
        result = subprocess.run(
            ["ufw", "status"], 
            capture_output=True, 
            text=True
        )

        firewall_output = result.stdout


        if "Status: active" in firewall_output:
            return {
                "Firewall":"Active"
            }
        else:
            return {
                "Firewall":"Inactive"
            }


    elif operating_system == "Darwin":
        pass



    


