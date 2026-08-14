# ============================================================
# SECURITY CHECKS MODULE
# ============================================================
# This module performs basic security-related checks on the
# computer.
#
# The checks include:
#
# - Administrator privileges on Windows
# - Root privileges on Linux/macOS
# - Listening network ports
# - Process associated with each listening port
# - PID associated with each listening process
# - Network exposure of each listening port
#
# A listening port is classified as:
#
# Localhost:
#     The service is only listening on the local computer.
#
# Network:
#     The service is listening on a network-accessible address.
#
# The number of network-exposed ports is later used by
# system_health.py to determine the security health of the
# system.
#
# Error handling is important in this module because some
# processes and network connections may be inaccessible due to
# operating-system permissions or may terminate while the scan
# is running.
#
# The results are returned as a dictionary so that they can be
# displayed by main.py and included in the diagnostic report.
# ============================================================


# ============================================================
# MODULE IMPORTS
# ============================================================
# The following modules provide the functionality required to
# perform the security checks.
# ============================================================


# platform identifies the operating system.
import platform


# ctypes is used on Windows to determine whether the current
# process has Administrator privileges.
import ctypes


# os provides access to the effective user ID on Unix-based
# operating systems such as Linux and macOS.
import os


# psutil provides access to:
#
# - Network connections
# - Listening ports
# - Process information
# - Process IDs
import psutil


# ============================================================
# RUN SECURITY CHECKS
# ============================================================
# Performs the security checks and returns the results.
# ============================================================

def run_security_checks():

    # Dictionary used to store security information.
    security_information = {}


    # ========================================================
    # DETERMINE OPERATING SYSTEM
    # ========================================================

    try:

        operating_system = platform.system()

    except Exception:

        operating_system = "Unknown"


    # ========================================================
    # CHECK ADMINISTRATOR / ROOT PRIVILEGES
    # ========================================================
    # Windows uses the Windows API to determine whether the
    # current process has Administrator privileges.
    #
    # Linux and macOS use the effective user ID.
    #
    # UID 0 represents the root account.
    # ========================================================

    if operating_system == "Windows":

        try:

            is_admin = ctypes.windll.shell32.IsUserAnAdmin()


            if is_admin:

                security_information[
                    "Administrator Privileges"
                ] = "Yes"

            else:

                security_information[
                    "Administrator Privileges"
                ] = "No"


        except Exception:

            security_information[
                "Administrator Privileges"
            ] = "Unable to determine"


    else:

        try:

            if os.geteuid() == 0:

                security_information[
                    "Root Privileges"
                ] = "Yes"

            else:

                security_information[
                    "Root Privileges"
                ] = "No"


        except AttributeError:

            security_information[
                "Root Privileges"
            ] = "Unable to determine"


        except Exception:

            security_information[
                "Root Privileges"
            ] = "Unable to determine"


    # ========================================================
    # LISTENING PORTS
    # ========================================================
    # psutil.net_connections(kind="inet") retrieves active
    # network connections using IPv4 and IPv6.
    #
    # We are specifically interested in connections with the
    # LISTEN status.
    #
    # These represent services waiting for incoming network
    # connections.
    # ========================================================

    listening_ports = []


    try:

        connections = psutil.net_connections(
            kind="inet"
        )

    except psutil.AccessDenied:

        security_information[
            "Listening Ports"
        ] = "Access Denied"

        return security_information


    except Exception:

        security_information[
            "Listening Ports"
        ] = "Unable to determine"

        return security_information


    # ========================================================
    # PROCESS LISTENING CONNECTIONS
    # ========================================================

    for connection in connections:

        try:

            # ------------------------------------------------
            # ONLY PROCESS LISTENING CONNECTIONS
            # ------------------------------------------------

            if connection.status != psutil.CONN_LISTEN:

                continue


            # ------------------------------------------------
            # MAKE SURE A LOCAL ADDRESS EXISTS
            # ------------------------------------------------

            if not connection.laddr:

                continue


            # =================================================
            # DEFAULT PROCESS INFORMATION
            # =================================================

            process_name = "Unknown"
            process_id = "Unknown"


            # =================================================
            # IDENTIFY PROCESS
            # =================================================
            # connection.pid identifies the process responsible
            # for the listening network connection.
            # =================================================

            if connection.pid:

                process_id = connection.pid


                try:

                    process = psutil.Process(
                        connection.pid
                    )

                    process_name = process.name()


                except (
                    psutil.NoSuchProcess,
                    psutil.AccessDenied,
                    psutil.ZombieProcess
                ):

                    process_name = "Unknown"


                except Exception:

                    process_name = "Unknown"


            # =================================================
            # DETERMINE LISTENING ADDRESS
            # =================================================

            address = connection.laddr.ip


            # =================================================
            # DETERMINE EXPOSURE
            # =================================================
            # 127.0.0.1 and ::1 are loopback addresses.
            #
            # Services listening on these addresses are only
            # accessible from the local computer.
            #
            # Other addresses are classified as Network because
            # they may be accessible from another device.
            # =================================================

            if address in (
                "127.0.0.1",
                "::1"
            ):

                exposure = "Localhost"

            else:

                exposure = "Network"


            # =================================================
            # STORE LISTENING PORT
            # =================================================

            listening_ports.append({

                "Address": (
                    f"{address}:"
                    f"{connection.laddr.port}"
                ),

                "Process": process_name,

                "PID": process_id,

                "Exposure": exposure

            })


        # =====================================================
        # CONNECTION ERROR HANDLING
        # =====================================================
        # A connection may disappear while it is being
        # processed. Ignore that individual connection and
        # continue checking the remaining connections.
        # =====================================================

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess
        ):

            continue


        except (
            AttributeError,
            TypeError,
            ValueError
        ):

            continue


        except Exception:

            continue


    # ========================================================
    # STORE LISTENING PORT INFORMATION
    # ========================================================
    # Even if no listening ports were found, an empty list is
    # returned. This allows system_health.py to correctly
    # identify the system as having no network-exposed ports.
    # ========================================================

    security_information[
        "Listening Ports"
    ] = listening_ports


    # ========================================================
    # RETURN SECURITY INFORMATION
    # ========================================================

    return security_information


# ============================================================
# STANDALONE TEST
# ============================================================
# Allows security_checks.py to be tested independently from
# main.py.
#
# This section only runs when the module is executed directly.
# ============================================================

if __name__ == "__main__":

    security_information = run_security_checks()


    print("SECURITY CHECKS")
    print("---------------")


    for key, value in security_information.items():

        if isinstance(value, list):

            print(f"\n{key}:")
            print("-" * 40)


            for item in value:

                for item_key, item_value in item.items():

                    print(
                        f"{item_key}: {item_value}"
                    )

                print()


        else:

            print(f"{key}: {value}")