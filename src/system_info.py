# ============================================================
# SYSTEM INFORMATION MODULE
# ============================================================
# This module collects basic information about the computer
# running the Secure IT Support Toolkit.
#
# The information collected includes:
#
# - Hostname
# - Operating System
# - OS Version
# - System Architecture
# - Processor
# - Current Username
# - Total RAM
# - Disk Usage
#
# The information is returned as a dictionary so that it can
# be displayed by main.py and included in the diagnostic report.
#
# Error handling is used throughout the module so that a failure
# to retrieve one piece of information does not cause the entire
# toolkit to stop running.
# ============================================================


# ============================================================
# MODULE IMPORTS
# ============================================================
# The following Python modules provide the functionality
# required to collect system information.
# ============================================================


# platform provides information about the operating system,
# operating system version, processor and system architecture.
import platform


# socket provides networking-related functionality.
# It is used here to retrieve the computer's hostname.
import socket


# psutil provides access to system and process information.
# It is used here to retrieve:
#
# - Total system RAM
# - Disk usage
#
# psutil is a third-party Python library.
import psutil


# getpass provides access to the username of the account
# running the program.
import getpass


# ============================================================
# GET SYSTEM INFORMATION
# ============================================================
# Collects system information and returns it as a dictionary.
#
# Each individual information-gathering operation has its own
# error handling so that one failure does not prevent the
# remaining information from being collected.
# ============================================================

def get_system_information():

    # Dictionary used to store all collected system information.
    system_info = {}


    # ========================================================
    # HOSTNAME
    # ========================================================
    # socket.gethostname() retrieves the name assigned to the
    # computer.
    # ========================================================

    try:

        system_info["Hostname"] = socket.gethostname()

    except Exception:

        system_info["Hostname"] = "Unable to determine"


    # ========================================================
    # OPERATING SYSTEM
    # ========================================================
    # platform.system() identifies the operating system.
    #
    # Typical results include:
    #
    # - Windows
    # - Linux
    # - Darwin (macOS)
    # ========================================================

    try:

        system_info["Operating System"] = platform.system()

    except Exception:

        system_info["Operating System"] = "Unable to determine"


    # ========================================================
    # OS VERSION
    # ========================================================
    # platform.version() retrieves operating system version
    # information.
    # ========================================================

    try:

        system_info["OS Version"] = platform.version()

    except Exception:

        system_info["OS Version"] = "Unable to determine"


    # ========================================================
    # SYSTEM ARCHITECTURE
    # ========================================================
    # platform.architecture() identifies whether the operating
    # system is running as 32-bit or 64-bit.
    # ========================================================

    try:

        system_info["Architecture"] = platform.architecture()[0]

    except Exception:

        system_info["Architecture"] = "Unable to determine"


    # ========================================================
    # PROCESSOR
    # ========================================================
    # platform.processor() attempts to retrieve information
    # about the system processor.
    #
    # Some operating systems may return an empty value, so an
    # empty result is treated as information that could not
    # be determined.
    # ========================================================

    try:

        processor = platform.processor()

        if processor:

            system_info["Processor"] = processor

        else:

            system_info["Processor"] = "Unable to determine"

    except Exception:

        system_info["Processor"] = "Unable to determine"


    # ========================================================
    # CURRENT USER
    # ========================================================
    # getpass.getuser() retrieves the username of the account
    # running the toolkit.
    # ========================================================

    try:

        system_info["Username"] = getpass.getuser()

    except Exception:

        system_info["Username"] = "Unable to determine"


    # ========================================================
    # RAM
    # ========================================================
    # psutil.virtual_memory() provides information about the
    # system's physical memory.
    #
    # The total memory is returned in bytes, so it is converted
    # into gigabytes before being added to the results.
    # ========================================================

    try:

        memory = psutil.virtual_memory()

        system_info["RAM"] = (
            f"{memory.total / (1024 ** 3):.2f} GB"
        )

    except Exception:

        system_info["RAM"] = "Unable to determine"


    # ========================================================
    # DISK USAGE
    # ========================================================
    # psutil.disk_usage() provides information about the
    # filesystem's total and used storage.
    #
    # Windows uses the C:\ drive as the primary system drive,
    # while Linux and macOS normally use /.
    #
    # The appropriate path is selected based on the operating
    # system.
    # ========================================================

    try:

        operating_system = platform.system()

        if operating_system == "Windows":

            disk_path = "C:\\"

        else:

            disk_path = "/"


        disk = psutil.disk_usage(disk_path)


        # Convert bytes into gigabytes and format the values
        # to two decimal places.

        system_info["Disk Usage"] = (
            f"{disk.used / (1024 ** 3):.2f} GB used "
            f"of {disk.total / (1024 ** 3):.2f} GB"
        )

    except Exception:

        system_info["Disk Usage"] = "Unable to determine"


    # ========================================================
    # RETURN SYSTEM INFORMATION
    # ========================================================
    # Returns the completed dictionary to the calling program.
    #
    # main.py can then:
    #
    # - Display the information to the user
    # - Store it in report_data
    # - Include it in the diagnostic report
    # ========================================================

    return system_info


# ============================================================
# STANDALONE TEST
# ============================================================
# This allows system_info.py to be tested independently from
# the main TechAssist application.
#
# The code below only runs when this file is executed directly.
# It does not run when the module is imported by main.py.
# ============================================================

if __name__ == "__main__":

    information = get_system_information()

    for item, value in information.items():

        print(f"{item}: {value}")