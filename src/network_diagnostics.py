# ============================================================
# NETWORK DIAGNOSTICS MODULE
# ============================================================
# This module performs several network troubleshooting checks.
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
# The module uses different commands where required to support
# Windows, Linux and macOS.
#
# The results are returned as a dictionary so that they can be
# displayed by main.py and included in the diagnostic report.
# ============================================================


# ============================================================
# MODULE IMPORTS
# ============================================================

# subprocess is used to execute operating-system networking
# commands such as ping, ipconfig, ip route and netstat.
import subprocess


# platform is used to identify the operating system so that
# the appropriate networking commands can be selected.
import platform


# socket provides DNS resolution functionality and networking
# constants such as AF_INET.
import socket


# psutil provides access to local network interface
# information.
import psutil


# ============================================================
# RUN NETWORK DIAGNOSTICS
# ============================================================
# Runs the complete set of network diagnostic checks and
# returns the results as a dictionary.
# ============================================================

def run_network_diagnostics():

    network_information = {}

    # Identify the operating system so that platform-specific
    # commands can be used later in the function.
    operating_system = platform.system()


    # ========================================================
    # INTERNET CONNECTIVITY
    # ========================================================
    # Test whether the computer can reach Google's public DNS
    # server at 8.8.8.8.
    #
    # A successful ping does not prove that every internet
    # service is working, but it provides a useful basic
    # connectivity test.
    #
    # Windows uses:
    #
    # ping -n 1
    #
    # Linux/macOS use:
    #
    # ping -c 1
    #
    # because the command-line options differ between platforms.
    # ========================================================

    if operating_system == "Windows":

        command = ["ping", "-n", "1", "8.8.8.8"]

    else:

        command = ["ping", "-c", "1", "8.8.8.8"]


    # Execute the ping command and capture its output so that
    # latency and packet-loss information can be extracted.
    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )


    # ========================================================
    # ANALYSE INTERNET CONNECTIVITY
    # ========================================================
    # subprocess.run() provides a returncode.
    #
    # A return code of 0 indicates that the command completed
    # successfully.
    # ========================================================

    if result.returncode == 0:

        network_information["Internet Connectivity"] = "Connected"


        # ====================================================
        # WINDOWS PING LATENCY
        # ====================================================
        # Windows formats the final ping statistics differently
        # from Linux, so the output needs to be parsed separately.
        # ====================================================

        if operating_system == "Windows":

            for line in result.stdout.splitlines():

                if "Average" in line:

                    latency = line.split(
                        "Average ="
                    )[-1].strip()

                    network_information["Ping Latency"] = latency

                    break


            # ------------------------------------------------
            # WINDOWS PACKET LOSS
            # ------------------------------------------------
            # Extract the packet-loss percentage from the
            # Windows ping summary.
            # ------------------------------------------------

            for line in result.stdout.splitlines():

                if "Lost =" in line:

                    packet_loss = (
                        line.split("(")[1]
                        .split(")")[0]
                    )

                    network_information["Packet Loss"] = packet_loss

                    break


        # ====================================================
        # LINUX PING LATENCY AND PACKET LOSS
        # ====================================================
        # Linux formats ping statistics differently from
        # Windows, so separate parsing is required.
        # ====================================================

        elif operating_system == "Linux":

            # ------------------------------------------------
            # Linux Ping Latency
            # ------------------------------------------------

            for line in result.stdout.splitlines():

                if "time=" in line:

                    latency = (
                        line.split("time=")[1]
                        .split()[0]
                    )

                    network_information["Ping Latency"] = (
                        f"{latency} ms"
                    )

                    break


            # ------------------------------------------------
            # Linux Packet Loss
            # ------------------------------------------------

            for line in result.stdout.splitlines():

                if "packet loss" in line:

                    packet_loss = (
                        line.split(",")[2]
                        .strip()
                        .replace(" packet loss", "")
                    )

                    network_information["Packet Loss"] = (
                        packet_loss
                    )

                    break


    # ========================================================
    # INTERNET CONNECTION FAILED
    # ========================================================
    # If the ping command returned a non-zero exit code, the
    # toolkit records the internet connection as disconnected.
    # ========================================================

    else:

        network_information["Internet Connectivity"] = (
            "Disconnected"
        )


    # ========================================================
    # DNS RESOLUTION
    # ========================================================
    # Test whether the computer can resolve a hostname to an
    # IP address.
    #
    # This helps distinguish between general connectivity
    # problems and DNS-specific problems.
    #
    # google.com is used as a simple, widely available hostname
    # for the test.
    # ========================================================

    try:

        socket.gethostbyname("www.google.com")

        network_information["DNS Resolution"] = "Working"

    except socket.gaierror:

        network_information["DNS Resolution"] = "Failed"


    # ========================================================
    # LOCAL IP ADDRESS
    # ========================================================
    # Examine the local network interfaces and find an IPv4
    # address that can be used for normal network communication.
    #
    # Loopback addresses (127.x.x.x) are excluded because they
    # refer to the local computer itself.
    #
    # Link-local/APIPA addresses (169.254.x.x) are also excluded
    # because they generally indicate that the device has not
    # obtained a normal address from DHCP.
    # ========================================================

    for interface, addresses in psutil.net_if_addrs().items():

        for address in addresses:

            if address.family == socket.AF_INET:

                if (
                    not address.address.startswith("127.")
                    and not address.address.startswith("169.254.")
                ):

                    network_information["Local IP Address"] = (
                        address.address
                    )

                    break


        # Stop searching once a suitable IPv4 address has been
        # found.
        if "Local IP Address" in network_information:

            break


    # ========================================================
    # DEFAULT GATEWAY - WINDOWS
    # ========================================================
    # Windows provides network configuration information through
    # the ipconfig command.
    #
    # The default gateway is extracted from the command output.
    # ========================================================

    if operating_system == "Windows":

        result = subprocess.run(
            ["ipconfig"],
            capture_output=True,
            text=True
        )

        for line in result.stdout.splitlines():

            if "Default Gateway" in line:

                gateway = line.split(":")[-1].strip()

                if gateway:

                    network_information["Default Gateway"] = (
                        gateway
                    )

                    break


    # ========================================================
    # DEFAULT GATEWAY - LINUX
    # ========================================================
    # Linux commonly provides routing information through:
    #
    # ip route
    #
    # A line containing "default via" identifies the default
    # gateway.
    # ========================================================

    elif operating_system == "Linux":

        result = subprocess.run(
            ["ip", "route"],
            capture_output=True,
            text=True
        )

        for line in result.stdout.splitlines():

            if "default via" in line:

                network_information["Default Gateway"] = (
                    line.split()[2]
                )

                break


    # ========================================================
    # DEFAULT GATEWAY - macOS
    # ========================================================
    # macOS can provide routing information using netstat.
    #
    # The routing table is examined to identify the default
    # gateway.
    # ========================================================

    elif operating_system == "Darwin":

        result = subprocess.run(
            ["netstat", "-rn"],
            capture_output=True,
            text=True
        )

        for line in result.stdout.splitlines():

            if line.startswith("gateway"):

                network_information["Default Gateway"] = (
                    line.split(":")[1].strip()
                )

                break


    # ========================================================
    # RETURN RESULTS
    # ========================================================
    # Return all collected network diagnostic information to
    # the calling program.
    #
    # main.py can then display these results and add them to
    # report_data for the diagnostic report.
    # ========================================================

    return network_information