# ============================================================
# DISK USAGE MODULE
# ============================================================
# This module collects information about the storage devices
# and filesystem partitions available on the computer.
#
# The information collected includes:
#
# - Mount Point
# - Device
# - Filesystem Type
# - Total Storage
# - Used Storage
# - Free Storage
# - Storage Usage Percentage
#
# The usage percentage is stored as a numeric value rather than
# including the "%" symbol. This allows the value to be used
# by other parts of the toolkit, such as system_health.py,
# where numerical thresholds are used to determine disk health.
#
# The report_generator.py module is responsible for adding the
# "%" symbol when the value is written to a diagnostic report.
#
# On Linux/WSL systems, certain internal mount points are
# excluded because they do not represent normal user storage.
#
# Error handling is used so that inaccessible partitions or
# unexpected filesystem information do not cause the entire
# toolkit to stop running.
# ============================================================


# ============================================================
# MODULE IMPORTS
# ============================================================
# The following modules provide the functionality required to
# collect disk information and identify the operating system.
# ============================================================


# psutil provides access to disk partitions and disk usage
# information.
import psutil


# platform identifies the operating system so that platform-
# specific filesystem exclusions can be applied.
import platform


# ============================================================
# GET DISK USAGE
# ============================================================
# Collects disk usage information for accessible filesystem
# partitions.
#
# The function returns a list of dictionaries, with each
# dictionary representing one filesystem partition.
# ============================================================

def get_disk_usage():

    # List used to store information about each accessible
    # filesystem partition.
    disk_information = []


    # ========================================================
    # RETRIEVE PARTITIONS
    # ========================================================
    # psutil.disk_partitions() retrieves the filesystem
    # partitions available on the system.
    #
    # If the information cannot be retrieved, an empty list is
    # returned rather than allowing the application to crash.
    # ========================================================

    try:

        partitions = psutil.disk_partitions()

    except Exception:

        return disk_information


    # Identify the operating system so that platform-specific
    # exclusions can be applied.
    try:

        operating_system = platform.system()

    except Exception:

        operating_system = "Unknown"


    # ========================================================
    # PROCESS EACH PARTITION
    # ========================================================
    # Each partition is processed individually.
    #
    # This means that a problem accessing one partition does
    # not prevent information from being collected from other
    # partitions.
    # ========================================================

    for partition in partitions:

        # ====================================================
        # SKIP WSL INTERNAL MOUNT POINTS
        # ====================================================
        # WSL can expose internal mount points that are not
        # useful when reporting normal disk usage.
        #
        # These are excluded from the results.
        # ====================================================

        if operating_system == "Linux":

            if partition.mountpoint.startswith("/mnt/wslg"):

                continue


            if partition.mountpoint.startswith("/var/lib/docker"):

                continue


        # ====================================================
        # RETRIEVE PARTITION USAGE
        # ====================================================
        # psutil.disk_usage() retrieves the total, used and
        # available storage for the selected mount point.
        # ====================================================

        try:

            usage = psutil.disk_usage(
                partition.mountpoint
            )


        # ----------------------------------------------------
        # PERMISSION ERROR
        # ----------------------------------------------------
        # Some partitions may not be accessible by the current
        # user. These partitions are skipped.
        # ----------------------------------------------------

        except PermissionError:

            continue


        # ----------------------------------------------------
        # FILESYSTEM / OS ERROR
        # ----------------------------------------------------
        # An OSError can occur if the filesystem is unavailable
        # or the mount point cannot be accessed.
        # ----------------------------------------------------

        except OSError:

            continue


        # ----------------------------------------------------
        # UNEXPECTED ERROR
        # ----------------------------------------------------
        # Prevents an unexpected problem with one partition
        # from terminating the entire disk diagnostic.
        # ----------------------------------------------------

        except Exception:

            continue


        # ====================================================
        # CONVERT STORAGE VALUES
        # ====================================================
        # psutil returns storage values in bytes.
        #
        # The toolkit converts these values into gigabytes
        # using 1024^3 bytes per gigabyte.
        # ====================================================

        try:

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


        except Exception:

            continue


        # ====================================================
        # STORE PARTITION INFORMATION
        # ====================================================
        # Usage remains numeric so that system_health.py can
        # compare it against numerical thresholds.
        #
        # Example:
        #
        # 46.5
        #
        # Rather than:
        #
        # "46.5 %"
        #
        # The percentage symbol is added later by the report
        # generator when required.
        # ====================================================

        try:

            disk_information.append({

                "Mount Point": partition.mountpoint,

                "Device": partition.device,

                "Filesystem Type": partition.fstype,

                "Total Space": f"{total_gb} GB",

                "Used Space": f"{used_gb} GB",

                "Free Space": f"{free_gb} GB",

                "Usage": usage.percent

            })


        except Exception:

            continue


    # ========================================================
    # RETURN DISK INFORMATION
    # ========================================================
    # Returns the completed list to the calling program.
    #
    # main.py can then:
    #
    # - Display the disk information
    # - Store it in report_data
    # - Pass it to system_health.py
    # - Include it in the diagnostic report
    # ========================================================

    return disk_information


# ============================================================
# STANDALONE TEST
# ============================================================
# This allows disk_usage.py to be tested independently from
# the main TechAssist application.
#
# The code below only runs when this file is executed directly.
# It does not run when the module is imported by main.py.
# ============================================================

if __name__ == "__main__":

    disk_information = get_disk_usage()


    print("DISK USAGE INFORMATION")
    print("----------------------")


    for index, drive in enumerate(
        disk_information,
        start=1
    ):

        print(f"\nDrive {index}:")
        print("----------")


        for key, value in drive.items():

            if key == "Usage":

                print(f"{key}: {value} %")

            else:

                print(f"{key}: {value}")