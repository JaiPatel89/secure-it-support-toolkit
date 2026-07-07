import platform
import socket
import psutil
import getpass


def get_system_information():
    
    system_info = {}
    
    system_info["Hostname"] = socket.gethostname()

    system_info["Operating System"] = platform.system()

    system_info["OS Version"] = platform.version()

    system_info["Architecture"] = platform.architecture()[0]

    system_info["Processor"] = platform.processor()

    system_info["Username"] = getpass.getuser()

    memory = psutil.virtual_memory()

    system_info["RAM"] = f"{memory.total / (1024 ** 3):.2f} GB"

    disk = psutil.disk_usage("/")

    system_info["Disk Usage"] = (
        f"{disk.used / (1024 ** 3):.2f} GB used "
        f"of {disk.total / (1024 ** 3):.2f} GB"
    )

    return system_info