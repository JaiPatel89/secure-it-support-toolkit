# ============================================================
# PROCESS MONITOR MODULE
# ============================================================
# This module collects information about currently running
# processes on the computer.
#
# The information collected includes:
#
# - Process Name
# - Process ID (PID)
# - Process Status
# - CPU Usage
# - Memory Usage
#
# Processes are sorted by memory usage and the top 10 processes
# are returned.
#
# This can help identify processes that are consuming a large
# amount of system memory and may be useful during IT support
# troubleshooting.
#
# Some processes may not be accessible because of permissions
# or because they terminate while the scan is running.
# These situations are handled so that one inaccessible process
# does not stop the entire process monitor.
#
# The information is returned as a list of dictionaries so that
# it can be displayed by main.py and included in the diagnostic
# report.
# ============================================================


# ============================================================
# MODULE IMPORTS
# ============================================================
# The following module provides access to running processes
# and system resource information.
# ============================================================


# psutil provides access to process information including:
#
# - Process names
# - PIDs
# - Process status
# - CPU usage
# - Memory usage
#
# psutil is a third-party Python library.
import psutil


# ============================================================
# GET PROCESSES
# ============================================================
# Collects information about running processes and returns the
# 10 processes using the most memory.
# ============================================================

def get_processes():

    # List used to store information about each accessible
    # process.
    process_information = []


    # ========================================================
    # PROCESS ITERATION
    # ========================================================
    # psutil.process_iter() allows the toolkit to retrieve
    # information about running processes.
    #
    # Only the fields required by this module are requested.
    # ========================================================

    try:

        processes = psutil.process_iter(
            {
                "pid",
                "name",
                "status",
                "memory_info"
            }
        )

    except Exception:

        return process_information


    # ========================================================
    # PROCESS EACH RUNNING PROCESS
    # ========================================================
    # Each process is handled individually.
    #
    # This is important because processes can terminate while
    # the scan is running or may not be accessible due to
    # permissions.
    # ========================================================

    for process in processes:

        try:

            # =================================================
            # MEMORY USAGE
            # =================================================
            # RSS (Resident Set Size) represents the amount of
            # physical memory currently being used by the
            # process.
            #
            # psutil reports memory in bytes, so it is converted
            # into megabytes.
            # =================================================

            memory_info = process.info["memory_info"]


            if memory_info is None:

                continue


            memory_mb = round(
                memory_info.rss / (1024 ** 2),
                2
            )


            # =================================================
            # CPU USAGE
            # =================================================
            # cpu_percent() returns the percentage of CPU time
            # being used by the process.
            #
            # interval=None allows the call to return without
            # deliberately waiting.
            # =================================================

            cpu_percent = process.cpu_percent(
                interval=None
            )


            # =================================================
            # STORE PROCESS INFORMATION
            # =================================================

            process_information.append({

                "Name": process.info["name"],

                "PID": process.info["pid"],

                "Status": process.info["status"],

                "CPU Usage": f"{cpu_percent}%",

                "Memory Usage (MB)": memory_mb

            })


        # =====================================================
        # PROCESS ERROR HANDLING
        # =====================================================
        # These exceptions can occur normally while monitoring
        # processes.
        #
        # NoSuchProcess:
        #     The process ended before its information could
        #     be collected.
        #
        # AccessDenied:
        #     The current user does not have permission to view
        #     the process.
        #
        # ZombieProcess:
        #     The process has terminated but still exists in
        #     the process table.
        # =====================================================

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess
        ):

            continue


        # =====================================================
        # GENERAL ERROR HANDLING
        # =====================================================
        # Protects the scan against an unexpected problem with
        # an individual process.
        # =====================================================

        except Exception:

            continue


    # ========================================================
    # SORT PROCESSES
    # ========================================================
    # Processes are sorted from highest to lowest memory usage.
    #
    # The numeric memory value is used for sorting so that:
    #
    # 100 MB
    #
    # correctly appears above:
    #
    # 20 MB
    # ========================================================

    try:

        process_information.sort(
            key=lambda x: x["Memory Usage (MB)"],
            reverse=True
        )

    except Exception:

        return process_information


    # ========================================================
    # RETURN TOP 10 PROCESSES
    # ========================================================
    # Only the 10 processes using the most memory are returned.
    # ========================================================

    return process_information[:10]


# ============================================================
# STANDALONE TEST
# ============================================================
# This allows process_monitor.py to be tested independently
# from the main TechAssist application.
#
# The code below only runs when this file is executed directly.
# It does not run when the module is imported by main.py.
# ============================================================

if __name__ == "__main__":

    process_information = get_processes()


    print("TOP 10 PROCESSES BY MEMORY USAGE")
    print("--------------------------------")


    for index, process in enumerate(
        process_information,
        start=1
    ):

        print(f"\nProcess {index}:")
        print("-------------")


        for key, value in process.items():

            print(f"{key}: {value}")