# ============================================================
# SYSTEM HEALTH MODULE
# ============================================================
# This module interprets diagnostic information collected by
# the other toolkit modules and converts it into simple health
# statuses.
#
# The module currently evaluates:
#
# - Disk usage
# - Firewall status
# - Administrator / root privileges
# - Network-exposed listening ports
# - Important system services
#
# Each area is classified as:
#
# Healthy
# Warning
# Critical
#
# The individual results are then combined to produce an
# overall system health status.
#
# IMPORTANT:
# The modules imported below collect the raw diagnostic data.
# This module is responsible for interpreting that data.
# ============================================================


# ============================================================
# MODULE IMPORTS
# ============================================================

# Used when this module is executed directly to collect disk
# usage information.
from disk_usage import get_disk_usage


# Used to collect the current firewall status.
from firewall_status import get_firewall_status


# Used to collect security information such as privileges and
# listening network ports.
from security_checks import run_security_checks


# Used to collect the status of important operating system
# services.
from service_status import get_service_status


# ============================================================
# DISK HEALTH
# ============================================================
# Evaluates disk usage and assigns a health status based on
# the percentage of storage currently being used.
#
# Thresholds:
#
# Below 80%  -> Healthy
# 80-89%     -> Warning
# 90%+       -> Critical
# ============================================================

def check_disk_health(disk_information):

    # List used to store the health result for each drive.
    disk_health = []


    # Evaluate each detected drive or partition.
    for drive in disk_information:

        # Retrieve the numeric disk usage percentage.
        usage = drive["Usage"]


        # 90% or more storage usage is considered critical.
        if usage >= 90:

            status = "Critical"


        # 80% to 89% storage usage generates a warning.
        elif usage >= 80:

            status = "Warning"


        # Anything below 80% is considered healthy.
        else:

            status = "Healthy"


        # Store the relevant information for this drive.
        disk_health.append({

            "Mount Point": drive["Mount Point"],

            "Usage": usage,

            "Status": status
        })


    # Return the health results for all drives.
    return disk_health


# ============================================================
# FIREWALL HEALTH
# ============================================================
# Evaluates the firewall status returned by firewall_status.py.
#
# A firewall that is enabled is considered Healthy.
#
# A firewall that is disabled or has another unexpected status
# is considered Critical.
# ============================================================

def check_firewall_health(firewall_information):

    # Dictionary used to store the health status for each
    # firewall profile.
    firewall_health = {}


    # Check each firewall profile or firewall status.
    for profile, status in firewall_information.items():

        # "on" is used by Windows, while "active" is used by
        # Linux/macOS in the current firewall module.
        if status.lower() in ["on", "active"]:

            firewall_health[profile] = "Healthy"


        # Anything other than an enabled firewall is considered
        # critical.
        else:

            firewall_health[profile] = "Critical"


    # Return the firewall health results.
    return firewall_health


# ============================================================
# SECURITY HEALTH
# ============================================================
# Evaluates security-related information collected by
# security_checks.py.
#
# The current checks include:
#
# - Administrator/root privileges
# - Network-exposed listening ports
# ============================================================

def check_security_health(security_information):

    # Dictionary used to store the security health results.
    security_health = {}


    # ========================================================
    # ADMINISTRATOR / ROOT PRIVILEGES
    # ========================================================
    # Running with elevated privileges is not automatically a
    # security problem, but the toolkit flags it as a warning
    # because unnecessary administrative/root privileges can
    # increase the potential impact of a compromised process.
    # ========================================================

    if "Administrator Privileges" in security_information:

        # A standard non-administrator Windows session is
        # considered healthy for this particular check.
        if security_information[
            "Administrator Privileges"
        ] == "No":

            security_health[
                "Administrator Privileges"
            ] = "Healthy"


        # Administrator privileges generate a warning.
        else:

            security_health[
                "Administrator Privileges"
            ] = "Warning"


    # Linux and macOS report root privileges instead.
    elif "Root Privileges" in security_information:

        # A non-root session is considered healthy.
        if security_information[
            "Root Privileges"
        ] == "No":

            security_health[
                "Root Privileges"
            ] = "Healthy"


        # Root privileges generate a warning.
        else:

            security_health[
                "Root Privileges"
            ] = "Warning"


    # ========================================================
    # LISTENING NETWORK PORTS
    # ========================================================
    # Count the listening ports that the security module has
    # classified as being exposed to the network.
    #
    # Localhost-only services are not counted as network-exposed
    # because they are bound to the local machine.
    # ========================================================

    listening_ports = security_information.get(
        "Listening Ports",
        []
    )


    # Counter for network-exposed listening ports.
    network_exposed = 0


    # Examine every listening port.
    for port in listening_ports:

        if port.get("Exposure") == "Network":

            network_exposed += 1


    # No network-exposed ports are considered healthy.
    if network_exposed == 0:

        security_health[
            "Network Exposed Ports"
        ] = "Healthy"


    # Any network-exposed ports currently generate a warning.
    else:

        security_health[
            "Network Exposed Ports"
        ] = (
            f"Warning - {network_exposed} exposed"
        )


    # Return the completed security health results.
    return security_health


# ============================================================
# SERVICE HEALTH
# ============================================================
# Converts service statuses into health statuses.
#
# Running service -> Healthy
# Stopped service -> Warning
#
# Other statuses are passed through unchanged.
# ============================================================

def check_service_health(service_information):

    # Dictionary used to store the health result for each
    # service.
    service_health = {}


    # Retrieve the service dictionary from the collected
    # service information.
    #
    # An empty dictionary is used if the expected key does not
    # exist.
    services = service_information.get(
        "Services",
        {}
    )


    # Evaluate every service.
    for service, status in services.items():

        # A running service is considered healthy.
        if status == "Running":

            service_health[service] = "Healthy"


        # A stopped service generates a warning.
        elif status == "Stopped":

            service_health[service] = "Warning"


        # Preserve unexpected statuses rather than making an
        # assumption about them.
        else:

            service_health[service] = status


    # Return the service health results.
    return service_health


# ============================================================
# CALCULATE OVERALL SYSTEM HEALTH
# ============================================================
# Combines the results from all health checks and determines
# the overall condition of the system.
#
# Priority:
#
# Critical
#    ↓
# Warning
#    ↓
# Healthy
#
# Therefore, a single Critical result makes the overall system
# Critical, while one or more Warnings make it Warning if
# there are no Critical results.
# ============================================================

def calculate_overall_health(
    disk_health,
    firewall_health,
    security_health,
    service_health
):

    # List used to collect every individual health status.
    statuses = []


    # ========================================================
    # DISK HEALTH
    # ========================================================

    for drive in disk_health:

        statuses.append(
            drive["Status"]
        )


    # ========================================================
    # FIREWALL HEALTH
    # ========================================================

    for status in firewall_health.values():

        statuses.append(status)


    # ========================================================
    # SECURITY HEALTH
    # ========================================================
    # Network exposed ports contain additional information,
    # for example:
    #
    # "Warning - 27 exposed"
    #
    # This needs to be converted into the standard "Warning"
    # status before it is added to the overall status list.
    # ========================================================

    for status in security_health.values():

        if status.startswith("Warning"):

            statuses.append("Warning")

        else:

            statuses.append(status)


    # ========================================================
    # SERVICE HEALTH
    # ========================================================

    for status in service_health.values():

        statuses.append(status)


    # ========================================================
    # DETERMINE OVERALL STATUS
    # ========================================================
    # Critical has the highest priority.
    #
    # If there are no Critical results, Warning has the next
    # highest priority.
    #
    # If neither exists, the system is considered Healthy.
    # ========================================================

    if "Critical" in statuses:

        return "Critical"


    elif "Warning" in statuses:

        return "Warning"


    else:

        return "Healthy"


# ============================================================
# STANDALONE MODULE TEST
# ============================================================
# This section allows system_health.py to be tested directly.
#
# It is only executed when this file is run directly.
#
# When system_health.py is imported by main.py, this section
# does not execute.
# ============================================================

if __name__ == "__main__":


    # ========================================================
    # DISK HEALTH TEST
    # ========================================================

    disk_information = get_disk_usage()

    disk_results = check_disk_health(
        disk_information
    )


    print("DISK HEALTH")
    print("-----------")


    for drive in disk_results:

        print(
            f"Mount Point: "
            f"{drive['Mount Point']}"
        )

        print(
            f"Usage: "
            f"{drive['Usage']} %"
        )

        print(
            f"Status: "
            f"{drive['Status']}"
        )

        print()


    # ========================================================
    # FIREWALL HEALTH TEST
    # ========================================================

    firewall_information = get_firewall_status()

    firewall_results = check_firewall_health(
        firewall_information
    )


    print("FIREWALL HEALTH")
    print("---------------")


    for profile, status in firewall_results.items():

        print(
            f"{profile}: {status}"
        )


    # ========================================================
    # SECURITY HEALTH TEST
    # ========================================================

    security_information = run_security_checks()

    security_results = check_security_health(
        security_information
    )


    print()
    print("SECURITY HEALTH")
    print("---------------")


    for check, status in security_results.items():

        print(
            f"{check}: {status}"
        )


    # ========================================================
    # SERVICE HEALTH TEST
    # ========================================================

    service_information = get_service_status()

    service_results = check_service_health(
        service_information
    )


    print()
    print("SERVICE HEALTH")
    print("--------------")


    for service, status in service_results.items():

        print(
            f"{service}: {status}"
        )


    # ========================================================
    # OVERALL SYSTEM HEALTH TEST
    # ========================================================

    overall_status = calculate_overall_health(
        disk_results,
        firewall_results,
        security_results,
        service_results
    )


    print()
    print("OVERALL SYSTEM HEALTH")
    print("---------------------")

    print(
        f"Status: {overall_status}"
    )