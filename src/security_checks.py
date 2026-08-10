import platform
import ctypes
import os
import psutil


def run_security_checks():

    security_information = {}

    operating_system = platform.system()

    if operating_system == "Windows":

        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()

            if is_admin:
                security_information["Administrator Privileges"] = "Yes"
            else:
                security_information["Administrator Privileges"] = "No"

        except Exception:
            security_information["Administrator Privileges"] = "Unable to determine"

    else:

        if os.geteuid() == 0:
            security_information["Root Privileges"] = "Yes"
        else:
            security_information["Root Privileges"] = "No"


    listening_ports = []

    for connection in psutil.net_connections(kind='inet'):

        if connection.status == psutil.CONN_LISTEN:

            if connection.laddr:

                process_name = "Unknown"
                process_id = "Unknown"

                if connection.pid:

                    process_pid = connection.pid

                    try:
                        process = psutil.Process(connection.pid)
                        process_name = process.name()

                    except (psutil.NoSuchProcess, psutil.AccessDenied):

                        process_name = "Unknown"

                address = connection.laddr.ip

                if address in ("127.0.0.1", "::1"):
                    exposure = "Localhost"
                else:
                    exposure = "Network"

                listening_ports.append({
                    "Address": f"{address}:{connection.laddr.port}",
                    "Process": process_name,
                    "PID": process_id,
                    "Exposure": exposure
                })

    security_information["Listening Ports"] = listening_ports
        


    return security_information