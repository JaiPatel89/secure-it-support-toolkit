# ============================================================
# SECURITY CHECKS MODULE
# ============================================================
# This module performs basic security checks on the local
# computer.
#
# The checks currently include:
#
# - Administrator/root privilege detection
# - Detection of listening network ports
# - Identification of the process using each listening port
# - Classification of whether a listening port is exposed
#   only to localhost or potentially to the network
#
# The results are returned as a dictionary so they can be
# displayed by main.py and included in diagnostic reports.
# ============================================================


# ============================================================
# MODULE IMPORTS
# ============================================================

# platform is used to identify the operating system so that
# Windows and Unix-like systems can use the appropriate
# privilege-checking method.
import platform


# ctypes provides access to Windows system functions.
#
# It is used here to call Windows' IsUserAnAdmin function.
import ctypes


# os provides access to operating-system functionality.
#
# On Linux and macOS, it is used to determine whether the
# current process is running with root privileges.
import os


# psutil provides access to network connections and running
# processes.
#
# It is used here to identify listening ports and the processes
# associated with them.
import psutil


# ============================================================
# RUN SECURITY CHECKS
# ============================================================
# Performs the security checks and returns the collected
# information.
# ============================================================

def run_security_checks():

    # Dictionary used to store the security results.
    security_information = {}


    # Identify the operating system.
    operating_system = platform.system()


    # ========================================================
    # WINDOWS ADMINISTRATOR PRIVILEGES
    # ========================================================
    # Windows provides the IsUserAnAdmin function for checking
    # whether the current process has administrator privileges.
    #
    # ctypes is used to access this Windows API function.
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


        # If the Windows API call cannot be completed, report
        # that the privilege level could not be determined.
        except Exception:

            security_information[
                "Administrator Privileges"
            ] = "Unable to determine"


    # ========================================================
    # LINUX / macOS ROOT PRIVILEGES
    # ========================================================
    # Linux and macOS use the Unix-style user ID system.
    #
    # UID 0 represents the root account.
    #
    # os.geteuid() returns the effective user ID of the current
    # process.
    # ========================================================

    else:

        if os.geteuid() == 0:

            security_information[
                "Root Privileges"
            ] = "Yes"

        else:

            security_information[
                "Root Privileges"
            ] = "No"


    # ========================================================
    # LISTENING NETWORK PORTS
    # ========================================================
    # A listening port represents a network socket that is
    # waiting for incoming connections.
    #
    # Listening services can be important during security and
    # troubleshooting investigations because they identify
    # services that may accept network connections.
    # ========================================================

    listening_ports = []


    # psutil.net_connections(kind='inet') retrieves IPv4 and
    # IPv6 network connections.
    #
    # Each connection can contain information such as:
    #
    # - Local address
    # - Port
    # - Connection status
    # - Process ID
    # ========================================================

    for connection in psutil.net_connections(
        kind='inet'
    ):


        # ====================================================
        # IDENTIFY LISTENING CONNECTIONS
        # ====================================================
        # Only connections in the LISTEN state are relevant
        # here because they are waiting for incoming network
        # connections.
        # ====================================================

        if connection.status == psutil.CONN_LISTEN:


            # Make sure a local address is available before
            # attempting to process the connection.

            if connection.laddr:


                # Default values are used in case the process
                # information cannot be retrieved.
                process_name = "Unknown"
                process_id = "Unknown"


                # =================================================
                # IDENTIFY ASSOCIATED PROCESS
                # =================================================
                # connection.pid identifies the process that owns
                # the listening socket.
                #
                # This allows the toolkit to associate a network
                # port with the application or service using it.
                # =================================================

                if connection.pid:

                    process_id = connection.pid


                    try:

                        process = psutil.Process(
                            connection.pid
                        )

                        process_name = process.name()


                    # A process can terminate or become
                    # inaccessible while the scan is running.
                    except (
                        psutil.NoSuchProcess,
                        psutil.AccessDenied
                    ):

                        process_name = "Unknown"


                # =================================================
                # DETERMINE NETWORK EXPOSURE
                # =================================================
                # The local IP address determines where the
                # service is listening.
                #
                # 127.0.0.1 and ::1 are loopback addresses.
                # Services listening only on these addresses are
                # accessible from the local machine but are not
                # directly exposed through the network interface.
                #
                # Other addresses are classified as "Network"
                # because they may accept connections from other
                # devices, depending on firewall and routing rules.
                # =================================================

                address = connection.laddr.ip


                if address in ("127.0.0.1", "::1"):

                    exposure = "Localhost"

                else:

                    exposure = "Network"


                # =================================================
                # STORE LISTENING PORT INFORMATION
                # =================================================
                # Store the address, associated process, PID and
                # exposure classification for later display and
                # reporting.
                # =================================================

                listening_ports.append({

                    "Address": (
                        f"{address}:{connection.laddr.port}"
                    ),

                    "Process": process_name,

                    "PID": process_id,

                    "Exposure": exposure
                })


    # ========================================================
    # STORE LISTENING PORT RESULTS
    # ========================================================
    # Add the complete list of listening ports to the security
    # information dictionary.
    # ========================================================

    security_information[
        "Listening Ports"
    ] = listening_ports


    # ========================================================
    # RETURN SECURITY RESULTS
    # ========================================================
    # Return the completed security information to the calling
    # program.
    # ========================================================

    return security_information