import psutil
import socket


def get_network_information():

    network_info = {}

    adapters = psutil.net_if_addrs()

    for adapter_name, addresses in adapters.items():
        
        ip_address = None
        MAC_address = None

        for address in addresses:

            if address.family == psutil.AF_LINK:
                MAC_address = address.address

            elif address.family == socket.AF_INET:
                if address.address != "127.0.0.1" and not address.address.startswith("169.254"):
                    ip_address = address.address
                
        if ip_address:
                network_info[adapter_name] = {
                    "IP Address": ip_address,
                    "MAC Address": MAC_address
                }
    
    return network_info