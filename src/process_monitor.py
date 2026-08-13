# ============================================================
# PROCESS MONITOR MODULE
# ============================================================
# This module collects information about currently running
# processes on the system.
#
# For each accessible process, it records:
#
# - Process name
# - Process ID (PID)
# - Process status
# - CPU usage
# - Memory usage
#
# The processes are sorted by memory usage and the top 10 are
# returned.
#
# This can be useful during IT troubleshooting when investigating
# high memory usage, resource consumption or an unresponsive
# system.
# ============================================================


# ============================================================
# MODULE IMPORTS
# ============================================================

# psutil provides access to running processes and their
# resource usage.
import psutil


# ============================================================
# GET PROCESSES
# ============================================================
# Collects information about currently running processes and
# returns the 10 processes using the most memory.
# ============================================================

def get_processes():

    # List used to store information about each process.
    process_information = []


    # ========================================================
    # ENUMERATE RUNNING PROCESSES
    # ========================================================
    # psutil.process_iter() provides an efficient way to
    # iterate through the processes currently running on
    # the system.
    #
    # The fields requested here are:
    #
    # - pid          Process ID
    # - name         Process name
    # - status       Current process status
    # - memory_info  Memory usage information
    #
    # Requesting only the required fields avoids collecting
    # unnecessary process information.
    # ========================================================

    for process in psutil.process_iter(
        {
            'pid',
            'name',
            'status',
            'memory_info'
        }
    ):


        # ====================================================
        # PROCESS INFORMATION
        # ====================================================
        # Access to individual processes can fail while the
        # program is running.
        #
        # For example:
        #
        # - A process may terminate during the scan.
        # - The current user may not have permission to inspect
        #   a process.
        # - A process may be a zombie process.
        #
        # These situations are handled below so that one
        # inaccessible process does not stop the entire monitor.
        # ====================================================

        try:


            # =================================================
            # MEMORY USAGE
            # =================================================
            # psutil reports RSS memory in bytes.
            #
            # RSS (Resident Set Size) represents the amount of
            # physical memory currently associated with the
            # process.
            #
            # Dividing by 1024^2 converts bytes into megabytes.
            #
            # The result is rounded to two decimal places.
            # =================================================

            memory_mb = round(
                process.info['memory_info'].rss
                / (1024 ** 2),
                2
            )


            # =================================================
            # CPU USAGE
            # =================================================
            # cpu_percent() provides the process's CPU usage.
            #
            # interval=None means the call does not wait for a
            # fixed measurement interval.
            #
            # The returned value is formatted with a percentage
            # sign before being added to the results.
            # =================================================

            cpu_percent = process.cpu_percent(
                interval=None
            )


            # =================================================
            # STORE PROCESS INFORMATION
            # =================================================
            # Add the process information to the results list.
            # =================================================

            process_information.append({

                "Name": process.info['name'],

                "PID": process.info['pid'],

                "Status": process.info['status'],

                "CPU Usage": f"{cpu_percent}%",

                "Memory Usage (MB)": memory_mb
            })


        # ====================================================
        # HANDLE PROCESS ACCESS ERRORS
        # ====================================================
        # Processes can disappear or become inaccessible while
        # they are being inspected.
        #
        # These exceptions are ignored and the monitor simply
        # continues with the next process.
        # ====================================================

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess
        ):

            continue


    # ========================================================
    # SORT PROCESSES BY MEMORY USAGE
    # ========================================================
    # Sort the collected processes using their memory usage.
    #
    # reverse=True places the highest memory-consuming process
    # first.
    # ========================================================

    process_information.sort(
        key=lambda x: x["Memory Usage (MB)"],
        reverse=True
    )


    # ========================================================
    # RETURN TOP 10 PROCESSES
    # ========================================================
    # Return only the first 10 processes after sorting.
    #
    # This keeps the toolkit's output manageable while
    # highlighting the processes consuming the most memory.
    # ========================================================

    return process_information[:10]