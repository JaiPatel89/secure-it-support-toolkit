import subprocess
import platform
import socket
import psutil


def run_network_diagnostics():

    network_information = {}

    operating_system = platform.system()

    #Check Internet Connectivity
    if operating_system == "Windows":
        command = ["ping", "-n", "1", "8.8.8.8"]

    else:
        command = ["ping", "-c", "1", "8.8.8.8"]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True
                    )


    if result.returncode == 0:
        network_information["Internet Connectivity"] = "Connected"

    else:
        network_information["Internet Connectivity"] = "Disconnected"

    #Check DNS Resolution
    try:
        socket.gethostbyname("www.google.com")
        network_information["DNS Resolution"] = "Working"

    except socket.gaierror:
        network_information["DNS Resolution"] = "Failed"


    for interface, addresses in psutil.net_if_addrs().items():

        for address in addresses:

            if address.family == socket.AF_INET:

                if (
                    not address.address.startswith("127.")
                    and not address.address.startswith("169.254.")
                ):

                    network_information["Local IP Address"] = address.address

                    break

        if "Local IP Address" in network_information:

            break


    if operating_system == "Windows":

        result = subprocess.run(
                ["ipconfig"],
                capture_output=True,
                text=True
            )

        for line in result.stdout.splitlines():

            if "Default Gateway" in line:

                gateway = line.split(":")[-1].strip()

                if gateway:

                    network_information["Default Gateway"] = gateway

                    break     


        
    elif operating_system == "Linux":

        result = subprocess.run(
                ["ip", "route"],
                capture_output=True,
                text=True
            )

        for line in result.stdout.splitlines():

            if "default via" in line:

                network_information["Default Gateway"] = line.split()[2]

                break

        

    elif operating_system == "Darwin":

        result = subprocess.run(
                ["netstat", "-rn"],
                capture_output=True,
                text=True
            )

        for line in result.stdout.splitlines():

            if line.startswith("gateway"):

                network_information["Default Gateway"] = line.split(":")[1].strip()

                break

    return network_information