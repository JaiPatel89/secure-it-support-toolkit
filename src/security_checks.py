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
# COMMON NETWORK PORTS
# ============================================================
# Maps common network ports to their typical services and
# explains why they may warrant review.
#
# These descriptions provide guidance only. A listed port
# is not automatically a security vulnerability.
# ============================================================

COMMON_PORTS = {

    22: {
        "Service": "SSH",
        "Review": "Check whether remote command-line access is required."
    },

    135: {
        "Service": "Windows RPC",
        "Review": "Check whether the service needs network access."
    },

    139: {
        "Service": "NetBIOS Session Service",
        "Review": "Check whether legacy file and printer sharing is required."
    },

    445: {
        "Service": "SMB",
        "Review": "Check file-sharing requirements and network restrictions."
    },

    1433: {
        "Service": "Microsoft SQL Server",
        "Review": "Check whether database access is appropriately restricted."
    },

    3306: {
        "Service": "MySQL",
        "Review": "Check whether database access is appropriately restricted."
    },

    3389: {
        "Service": "Remote Desktop Protocol (RDP)",
        "Review": "Check whether remote desktop access is required and restricted."
    },

    5432: {
        "Service": "PostgreSQL",
        "Review": "Check whether database access is appropriately restricted."
    },

    5900: {
        "Service": "VNC",
        "Review": "Check whether remote desktop access is required and restricted."
    },

    8080: {
        "Service": "Alternative HTTP service",
        "Review": "Check which application is using this port."
    }

}




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
            # IDENTIFY COMMON PORT SERVICE
            # =================================================

            port_number = connection.laddr.port

            port_information = COMMON_PORTS.get(
                port_number,
                {
                    "Service": "Unlisted service",
                    "Review": (
                        "Review the process and determine "
                        "whether this port is required."
                    )
                }
            )


            # =================================================
            # STORE LISTENING PORT
            # =================================================

            listening_ports.append({

                "Address": (
                    f"{address}:"
                    f"{port_number}"
                ),

                "Port": port_number,

                "Service": port_information["Service"],

                "Review": port_information["Review"],

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
    # SUMMARISE LISTENING PORTS
    # ========================================================
    # Count the listening ports and group them by their
    # detected listening address.
    #
    # Network-bound listeners may be reachable from other
    # devices, but this check does not confirm accessibility.
    # ========================================================

    total_listening_ports = len(listening_ports)

    localhost_listeners = sum(
        1
        for port in listening_ports
        if port["Exposure"] == "Localhost"
    )

    network_bound_listeners = sum(
        1
        for port in listening_ports
        if port["Exposure"] == "Network"
    )


    # ========================================================
    # STORE SUMMARY INFORMATION
    # ========================================================

    security_information[
        "Total Listening Ports"
    ] = total_listening_ports

    security_information[
        "Localhost Listeners"
    ] = localhost_listeners

    security_information[
        "Network-Bound Listeners"
    ] = network_bound_listeners


    # ========================================================
    # STORE LISTENING PORT DETAILS
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