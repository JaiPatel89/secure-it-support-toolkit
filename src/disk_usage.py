# ============================================================
# DISK USAGE MODULE
# ============================================================
# This module collects storage information for the disks and
# partitions detected on the system.
#
# The information collected includes:
#
# - Mount point
# - Device
# - Filesystem type
# - Total storage
# - Used storage
# - Free storage
# - Percentage of storage currently in use
#
# The module also contains handling for WSL-specific mount
# points and permission-restricted filesystems.
#
# The results are returned as a list of dictionaries so that
# multiple drives or partitions can be represented.
# ============================================================


# ============================================================
# MODULE IMPORTS
# ============================================================

# psutil provides access to disk partitions and disk usage.
import psutil


# platform is used to determine the operating system so that
# Linux-specific WSL mount points can be excluded.
import platform


# ============================================================
# GET DISK USAGE
# ============================================================
# Collects storage information for available disks and
# partitions.
# ============================================================

def get_disk_usage():

    # List used to store information about each detected
    # partition.
    disk_information = []


    # Retrieve the partitions currently detected by the
    # operating system.
    partitions = psutil.disk_partitions()


    # Identify the operating system.
    operating_system = platform.system()


    # ========================================================
    # PROCESS EACH PARTITION
    # ========================================================

    for partition in partitions:


        # ====================================================
        # WSL MOUNT POINT FILTERING
        # ====================================================
        # When the toolkit is running under Linux/WSL,
        # psutil can detect internal WSL and Docker mount
        # points that are not useful for normal disk reporting.
        #
        # These are excluded to keep the diagnostic output
        # focused on useful storage devices.
        # ====================================================

        if operating_system == "Linux":

            # Exclude WSLg internal mount points.
            if partition.mountpoint.startswith("/mnt/wslg"):
                continue


            # Exclude Docker's internal storage mount point.
            if partition.mountpoint.startswith("/var/lib/docker"):
                continue


        # ====================================================
        # GET PARTITION USAGE
        # ====================================================
        # psutil.disk_usage() retrieves the storage statistics
        # for the current partition.
        #
        # Some filesystems may not be accessible due to
        # permissions. A PermissionError is therefore handled
        # so that one inaccessible partition does not cause the
        # entire diagnostic program to fail.
        # ====================================================

        try:

            usage = psutil.disk_usage(
                partition.mountpoint
            )

        except PermissionError:

            # Skip partitions that cannot be accessed.
            continue


        # ====================================================
        # CONVERT STORAGE VALUES
        # ====================================================
        # psutil reports storage sizes in bytes.
        #
        # Dividing by 1024^3 converts bytes into gigabytes.
        #
        # round(..., 2) limits the displayed values to two
        # decimal places.
        # ====================================================

        total_gb = round(
            usage.total / (1024 ** 3),
            2
        )

        used_gb = round(
            usage.used / (1024 ** 3),
            2
        )

        free_gb = round(
            usage.free / (1024 ** 3),
            2
        )


        # ====================================================
        # STORE PARTITION INFORMATION
        # ====================================================
        # Each partition is represented as a dictionary.
        #
        # A list of dictionaries allows the module to return
        # information for multiple drives or partitions.
        # ====================================================

        disk_information.append({

            "Mount Point": partition.mountpoint,

            "Device": partition.device,

            "Filesystem Type": partition.fstype,

            "Total Space": f"{total_gb} GB",

            "Used Space": f"{used_gb} GB",

            "Free Space": f"{free_gb} GB",

            # psutil already provides the usage percentage,
            # so the numeric value is stored directly here.
            #
            # main.py and report_generator.py add the "%"
            # symbol when displaying the value.
            "Usage": usage.percent
        })


    # ========================================================
    # RETURN RESULTS
    # ========================================================
    # Return the completed list to the calling program.
    # ========================================================

    return disk_information