# ============================================================
# NETWORK DIAGNOSTICS MODULE
# ============================================================
# This module performs several network diagnostic checks.
#
# The checks include:
#
# - Internet connectivity
# - Ping latency
# - Packet loss
# - DNS resolution
# - Local IP address
# - Default gateway
#
# Windows, Linux and macOS use different commands for some
# network diagnostics, so the appropriate command is selected
# based on the operating system.
#
# The results are returned as a dictionary so that they can be
# displayed by main.py and included in the diagnostic report.
#
# Error handling is included so that a failed diagnostic does
# not cause the entire TechAssist application to stop.
# ============================================================


# ============================================================
# MODULE IMPORTS
# ============================================================
# subprocess:
#     Executes operating-system network commands.
#
# platform:
#     Identifies the operating system.
#
# socket:
#     Provides DNS resolution and IPv4 constants.
#
# psutil:
#     Provides information about network interfaces.
# ============================================================

import subprocess
import platform
import socket
import psutil


# ============================================================
# RUN NETWORK DIAGNOSTICS
# ============================================================
# Performs the network diagnostic checks and returns the
# results as a dictionary.
# ============================================================

def run_network_diagnostics():

    network_information = {}

    operating_system = platform.system()


    # ========================================================
    # CHECK INTERNET CONNECTIVITY
    # ========================================================
    # Windows uses:
    #
    # ping -n 1 8.8.8.8
    #
    # Linux/macOS use:
    #
    # ping -c 1 8.8.8.8
    # ========================================================

    if operating_system == "Windows":

        command = [
            "ping",
            "-n",
            "1",
            "8.8.8.8"
        ]

    else:

        command = [
            "ping",
            "-c",
            "1",
            "8.8.8.8"
        ]


    try:

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=10
        )


    except FileNotFoundError:

        network_information["Internet Connectivity"] = (
            "Command Unavailable"
        )

        result = None


    except subprocess.TimeoutExpired:

        network_information["Internet Connectivity"] = (
            "Command Timed Out"
        )

        result = None


    except Exception as error:

        network_information["Internet Connectivity"] = (
            "Unable to determine"
        )

        result = None


    # ========================================================
    # PROCESS PING RESULT
    # ========================================================

    if result is not None:

        if result.returncode == 0:

            network_information["Internet Connectivity"] = (
                "Connected"
            )


            # =================================================
            # WINDOWS PING INFORMATION
            # =================================================

            if operating_system == "Windows":

                for line in result.stdout.splitlines():

                    if "Average" in line:

                        try:

                            latency = (
                                line
                                .split("Average =")[-1]
                                .strip()
                            )

                            network_information[
                                "Ping Latency"
                            ] = latency

                        except Exception:

                            pass

                        break


                for line in result.stdout.splitlines():

                    if "Lost =" in line:

                        try:

                            packet_loss = (
                                line
                                .split("(")[1]
                                .split(")")[0]
                            )

                            network_information[
                                "Packet Loss"
                            ] = packet_loss

                        except (IndexError, ValueError):

                            pass

                        break


            # =================================================
            # LINUX / macOS PING INFORMATION
            # =================================================

            elif (
                operating_system == "Linux"
                or operating_system == "Darwin"
            ):

                for line in result.stdout.splitlines():

                    if "time=" in line:

                        try:

                            latency = (
                                line
                                .split("time=")[1]
                                .split()[0]
                            )

                            network_information[
                                "Ping Latency"
                            ] = f"{latency} ms"

                        except (IndexError, ValueError):

                            pass

                        break


                for line in result.stdout.splitlines():

                    if "packet loss" in line:

                        try:

                            packet_loss = (
                                line
                                .split(",")[2]
                                .strip()
                                .replace(
                                    " packet loss",
                                    ""
                                )
                            )

                            network_information[
                                "Packet Loss"
                            ] = packet_loss

                        except (IndexError, ValueError):

                            pass

                        break


        else:

            network_information["Internet Connectivity"] = (
                "Disconnected"
            )


    # ========================================================
    # CHECK DNS RESOLUTION
    # ========================================================
    # Attempts to resolve www.google.com.
    #
    # Successful resolution indicates that DNS is working.
    # ========================================================

    try:

        socket.gethostbyname("www.google.com")

        network_information["DNS Resolution"] = "Working"


    except socket.gaierror:

        network_information["DNS Resolution"] = "Failed"


    except Exception:

        network_information["DNS Resolution"] = (
            "Unable to determine"
        )


    # ========================================================
    # FIND LOCAL IP ADDRESS
    # ========================================================
    # Searches network interfaces for a usable IPv4 address.
    #
    # Loopback addresses and APIPA addresses are ignored.
    # ========================================================

    try:

        adapters = psutil.net_if_addrs()

    except Exception:

        adapters = {}


    for interface, addresses in adapters.items():

        try:

            for address in addresses:

                if address.family == socket.AF_INET:

                    if (
                        not address.address.startswith("127.")
                        and not address.address.startswith(
                            "169.254."
                        )
                    ):

                        network_information[
                            "Local IP Address"
                        ] = address.address

                        break


            if "Local IP Address" in network_information:

                break


        except Exception:

            continue


    # ========================================================
    # FIND DEFAULT GATEWAY - WINDOWS
    # ========================================================
    # Windows uses ipconfig to retrieve the default gateway.
    # ========================================================

    if operating_system == "Windows":

        try:

            result = subprocess.run(
                ["ipconfig"],
                capture_output=True,
                text=True,
                timeout=10
            )


            for line in result.stdout.splitlines():

                if "Default Gateway" in line:

                    gateway = (
                        line
                        .split(":")[-1]
                        .strip()
                    )

                    if gateway:

                        network_information[
                            "Default Gateway"
                        ] = gateway

                        break


        except (
            FileNotFoundError,
            subprocess.TimeoutExpired
        ):

            pass

        except Exception:

            pass


    # ========================================================
    # FIND DEFAULT GATEWAY - LINUX
    # ========================================================

    elif operating_system == "Linux":

        try:

            result = subprocess.run(
                ["ip", "route"],
                capture_output=True,
                text=True,
                timeout=10
            )


            for line in result.stdout.splitlines():

                if "default via" in line:

                    try:

                        network_information[
                            "Default Gateway"
                        ] = line.split()[2]

                    except IndexError:

                        pass

                    break


        except (
            FileNotFoundError,
            subprocess.TimeoutExpired
        ):

            pass

        except Exception:

            pass


    # ========================================================
    # FIND DEFAULT GATEWAY - macOS
    # ========================================================

    elif operating_system == "Darwin":

        try:

            result = subprocess.run(
                ["netstat", "-rn"],
                capture_output=True,
                text=True,
                timeout=10
            )


            for line in result.stdout.splitlines():

                if line.startswith("gateway"):

                    try:

                        network_information[
                            "Default Gateway"
                        ] = (
                            line
                            .split(":")[1]
                            .strip()
                        )

                    except (IndexError, ValueError):

                        pass

                    break


        except (
            FileNotFoundError,
            subprocess.TimeoutExpired
        ):

            pass

        except Exception:

            pass


    # ========================================================
    # RETURN NETWORK INFORMATION
    # ========================================================
    # Returns all successfully collected diagnostic results.
    # ========================================================

    return network_information


# ============================================================
# STANDALONE TEST
# ============================================================
# Allows this module to be tested independently from main.py.
#
# This section only executes when the file itself is run.
# ============================================================

if __name__ == "__main__":

    print("Running network diagnostics...")
    print()

    network_information = run_network_diagnostics()

    print("NETWORK DIAGNOSTICS")
    print("-------------------")

    for item, value in network_information.items():

        print(f"{item}: {value}")