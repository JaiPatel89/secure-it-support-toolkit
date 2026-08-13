# ============================================================
# NETWORK INFORMATION MODULE
# ============================================================
# This module collects basic network adapter information from
# the local computer.
#
# For each active adapter with a usable IPv4 address, the
# module attempts to identify:
#
# - IP Address
# - MAC Address
#
# Loopback and automatically assigned link-local IPv4
# addresses are excluded because they are not useful when
# identifying a normal network connection.
#
# The information is returned as a dictionary so that it can
# be displayed by main.py and included in diagnostic reports.
# ============================================================


# ============================================================
# MODULE IMPORTS
# ============================================================

# psutil provides access to network interface information,
# including adapter addresses and MAC addresses.
import psutil


# socket provides networking constants such as AF_INET,
# which identifies IPv4 addresses.
import socket


# ============================================================
# GET NETWORK INFORMATION
# ============================================================
# Collects IP and MAC address information for the system's
# network adapters.
# ============================================================

def get_network_information():

    # Dictionary used to store the network information that
    # will eventually be returned to the main program.
    network_info = {}


    # --------------------------------------------------------
    # GET NETWORK ADAPTERS
    # --------------------------------------------------------
    # psutil.net_if_addrs() returns the addresses associated
    # with each network interface on the system.
    #
    # The result can contain multiple addresses for a single
    # adapter, including:
    #
    # - IPv4 addresses
    # - IPv6 addresses
    # - MAC addresses
    # --------------------------------------------------------

    adapters = psutil.net_if_addrs()


    # ========================================================
    # PROCESS EACH NETWORK ADAPTER
    # ========================================================

    for adapter_name, addresses in adapters.items():

        # These variables are reset for each adapter.
        ip_address = None
        MAC_address = None


        # ----------------------------------------------------
        # PROCESS ADDRESSES ASSOCIATED WITH THE ADAPTER
        # ----------------------------------------------------

        for address in addresses:


            # =================================================
            # MAC ADDRESS
            # =================================================
            # psutil.AF_LINK identifies a hardware/network
            # interface address such as a MAC address.
            # =================================================

            if address.family == psutil.AF_LINK:

                MAC_address = address.address


            # =================================================
            # IPv4 ADDRESS
            # =================================================
            # socket.AF_INET identifies an IPv4 address.
            # =================================================

            elif address.family == socket.AF_INET:

                # ------------------------------------------------
                # Exclude loopback addresses
                # ------------------------------------------------
                # 127.0.0.1 refers to the local computer itself
                # and is not a usable address for communicating
                # with other devices on the network.
                #
                # Exclude 169.254.x.x addresses
                # ------------------------------------------------
                # Addresses beginning with 169.254 are IPv4
                # link-local/APIPA addresses.
                #
                # Windows can assign these automatically when
                # a device cannot obtain an address from DHCP.
                #
                # These addresses are therefore excluded from
                # the main network information output.
                # ------------------------------------------------

                if (
                    address.address != "127.0.0.1"
                    and not address.address.startswith("169.254")
                ):

                    ip_address = address.address


        # ====================================================
        # STORE ADAPTER INFORMATION
        # ====================================================
        # Only adapters with a usable IPv4 address are included
        # in the final results.
        #
        # This prevents disconnected or non-network interfaces
        # from unnecessarily appearing in the output.
        # ====================================================

        if ip_address:

            network_info[adapter_name] = {
                "IP Address": ip_address,
                "MAC Address": MAC_address
            }


    # ========================================================
    # RETURN NETWORK INFORMATION
    # ========================================================
    # Return the completed dictionary to the calling program.
    # ========================================================

    return network_info