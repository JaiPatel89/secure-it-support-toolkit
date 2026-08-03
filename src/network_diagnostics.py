import subprocess
import platform
import socket


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

    return network_information