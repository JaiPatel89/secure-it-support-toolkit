# ============================================================
# NETWORK INFORMATION MODULE
# ============================================================
# This module collects information about the network adapters
# available on the computer.
#
# The information collected includes:
#
# - Network adapter name
# - IPv4 address
# - MAC address
#
# Loopback addresses such as 127.0.0.1 are ignored because they
# represent the local computer rather than a normal network
# connection.
#
# APIPA addresses beginning with 169.254 are also ignored.
# These addresses are normally assigned automatically when an
# adapter cannot obtain an address from DHCP.
#
# Only adapters with a usable IPv4 address are included in the
# results.
#
# The information is returned as a dictionary so that it can be
# displayed by main.py and included in the diagnostic report.
#
# Error handling is used so that a problem retrieving network
# information does not cause the entire toolkit to stop.
# ============================================================


# ============================================================
# MODULE IMPORTS
# ============================================================
# The following modules provide the functionality required to
# collect network adapter information.
# ============================================================


# psutil provides access to network interface information.
# It is used to retrieve network adapters, IP addresses and
# MAC addresses.
import psutil


# socket provides networking-related constants.
# AF_INET is used to identify IPv4 addresses.
import socket


# ============================================================
# GET NETWORK INFORMATION
# ============================================================
# Collects information about the available network adapters.
#
# The function returns a dictionary containing the adapter name,
# IPv4 address and MAC address for each usable adapter.
# ============================================================

def get_network_information():

    # Dictionary used to store network adapter information.
    network_info = {}


    # ========================================================
    # RETRIEVE NETWORK ADAPTERS
    # ========================================================
    # psutil.net_if_addrs() retrieves the addresses assigned
    # to each network interface.
    #
    # If the information cannot be retrieved, an empty
    # dictionary is returned instead of allowing the program
    # to crash.
    # ========================================================

    try:

        adapters = psutil.net_if_addrs()

    except Exception:

        return network_info


    # ========================================================
    # PROCESS NETWORK ADAPTERS
    # ========================================================
    # Each network adapter is processed individually.
    #
    # This allows the function to continue processing other
    # adapters if one adapter contains unexpected information.
    # ========================================================

    for adapter_name, addresses in adapters.items():

        try:

            # Variables used to store the relevant addresses.
            ip_address = None
            MAC_address = None


            # =================================================
            # PROCESS ADDRESSES
            # =================================================
            # Each adapter can have multiple addresses.
            #
            # We are specifically interested in:
            #
            # - IPv4 addresses
            # - MAC addresses
            # =================================================

            for address in addresses:


                # ------------------------------------------------
                # MAC ADDRESS
                # ------------------------------------------------
                # psutil.AF_LINK identifies a link-layer address,
                # such as a MAC address.
                # ------------------------------------------------

                if address.family == psutil.AF_LINK:

                    MAC_address = address.address


                # ------------------------------------------------
                # IPv4 ADDRESS
                # ------------------------------------------------
                # socket.AF_INET identifies an IPv4 address.
                #
                # Loopback and APIPA addresses are ignored.
                # ------------------------------------------------

                elif address.family == socket.AF_INET:

                    if (
                        address.address != "127.0.0.1"
                        and not address.address.startswith("169.254")
                    ):

                        ip_address = address.address


            # =================================================
            # STORE ADAPTER INFORMATION
            # =================================================
            # Only adapters with a usable IPv4 address are
            # included in the returned results.
            # =================================================

            if ip_address:

                network_info[adapter_name] = {
                    "IP Address": ip_address,
                    "MAC Address": MAC_address
                }


        # =====================================================
        # ADAPTER ERROR HANDLING
        # =====================================================
        # If an individual adapter cannot be processed, skip
        # it and continue checking the remaining adapters.
        # =====================================================

        except (
            AttributeError,
            TypeError,
            ValueError
        ):

            continue

        except Exception:

            continue


    # ========================================================
    # RETURN NETWORK INFORMATION
    # ========================================================
    # Returns the completed dictionary to the calling program.
    #
    # main.py can then:
    #
    # - Display the network information
    # - Store it in report_data
    # - Include it in the diagnostic report
    # ========================================================

    return network_info


# ============================================================
# STANDALONE TEST
# ============================================================
# This allows network_tools.py to be tested independently from
# the main TechAssist application.
#
# The code below only runs when this file is executed directly.
# It does not run when the module is imported by main.py.
# ============================================================

if __name__ == "__main__":

    network_information = get_network_information()


    # Display each detected network adapter and its information.

    for adapter, details in network_information.items():

        print(f"Adapter: {adapter}")

        for detail_name, detail_value in details.items():

            print(f"{detail_name}: {detail_value}")

        print()