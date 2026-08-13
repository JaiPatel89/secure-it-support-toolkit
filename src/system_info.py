# ============================================================
# SYSTEM INFORMATION MODULE
# ============================================================
# This module collects basic information about the computer
# running the Secure IT Support Toolkit.
#
# The information collected can be useful during IT support
# and troubleshooting because it provides a quick overview
# of the system's hardware, operating system and current user.
#
# The module is designed to work across multiple operating
# systems by using Python's cross-platform libraries where
# possible.
# ============================================================


# ============================================================
# MODULE IMPORTS
# ============================================================

# platform
# Provides operating-system and hardware information such as
# the OS name, OS version, processor and system architecture.
import platform


# socket
# Used here to retrieve the computer's hostname.
import socket


# psutil
# Provides access to system information such as RAM and disk
# usage.
#
# psutil is a third-party Python library and is used throughout
# this project for system monitoring functionality.
import psutil


# getpass
# Used to determine the username of the account currently
# running the toolkit.
import getpass


# ============================================================
# GET SYSTEM INFORMATION
# ============================================================
# Collects the main system information required by the
# toolkit and returns it as a dictionary.
#
# Returning a dictionary makes the information easy to:
#
# - Display in the main menu
# - Store in report_data
# - Include in the diagnostic report
# - Reuse by other modules if required
# ============================================================

def get_system_information():

    system_info = {}


    # ========================================================
    # HOSTNAME
    # ========================================================
    # socket.gethostname() returns the network hostname of
    # the computer.
    #
    # This can help identify which machine a diagnostic report
    # was generated from.
    # ========================================================

    system_info["Hostname"] = socket.gethostname()


    # ========================================================
    # OPERATING SYSTEM
    # ========================================================
    # platform.system() identifies the operating system.
    #
    # Typical results include:
    #
    # Windows
    # Linux
    # Darwin
    #
    # Darwin is the value returned for macOS.
    # ========================================================

    system_info["Operating System"] = platform.system()


    # ========================================================
    # OPERATING SYSTEM VERSION
    # ========================================================
    # platform.version() provides the operating system's
    # underlying version/build information.
    #
    # This can be useful when troubleshooting software or
    # compatibility issues.
    # ========================================================

    system_info["OS Version"] = platform.version()


    # ========================================================
    # SYSTEM ARCHITECTURE
    # ========================================================
    # platform.architecture() identifies whether the Python
    # environment is running as 32-bit or 64-bit.
    #
    # [0] selects the architecture value from the tuple
    # returned by platform.architecture().
    # ========================================================

    system_info["Architecture"] = platform.architecture()[0]


    # ========================================================
    # PROCESSOR
    # ========================================================
    # platform.processor() attempts to return information
    # identifying the system processor.
    #
    # The exact information returned can vary between operating
    # systems and hardware.
    # ========================================================

    system_info["Processor"] = platform.processor()


    # ========================================================
    # CURRENT USER
    # ========================================================
    # getpass.getuser() returns the username associated with
    # the account running the program.
    #
    # This can be useful when investigating permissions or
    # identifying which user generated a diagnostic report.
    # ========================================================

    system_info["Username"] = getpass.getuser()


    # ========================================================
    # RAM
    # ========================================================
    # psutil.virtual_memory() retrieves information about the
    # system's physical memory.
    #
    # memory.total contains the total amount of installed
    # memory in bytes.
    #
    # Dividing by 1024^3 converts bytes into gigabytes.
    #
    # :.2f limits the displayed value to two decimal places.
    # ========================================================

    memory = psutil.virtual_memory()

    system_info["RAM"] = (
        f"{memory.total / (1024 ** 3):.2f} GB"
    )


    # ========================================================
    # DISK USAGE
    # ========================================================
    # psutil.disk_usage("/") retrieves disk information for
    # the root filesystem.
    #
    # The returned information includes:
    #
    # - Total disk capacity
    # - Used disk space
    # - Free disk space
    #
    # The values returned by psutil are in bytes, so they are
    # converted to gigabytes before being displayed.
    # ========================================================

    disk = psutil.disk_usage("/")


    system_info["Disk Usage"] = (
        f"{disk.used / (1024 ** 3):.2f} GB used "
        f"of {disk.total / (1024 ** 3):.2f} GB"
    )


    # ========================================================
    # RETURN RESULTS
    # ========================================================
    # Return the completed dictionary to the calling function.
    #
    # The main program can then display the information and
    # store it in the diagnostic report.
    # ========================================================

    return system_info