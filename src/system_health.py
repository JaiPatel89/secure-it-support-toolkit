# ============================================================
# SYSTEM HEALTH MODULE
# ============================================================
# This module evaluates the results produced by the other
# diagnostic modules and converts them into an overall health
# assessment.
#
# The module checks:
#
# - Disk Health
# - Firewall Health
# - Security Health
# - Service Health
# - Overall System Health
#
# Each area is assigned a status:
#
#     Healthy
#     Warning
#     Critical
#
# The overall system health is determined using the following
# priority:
#
#     Critical
#         ↓
#     Warning
#         ↓
#     Healthy
#
# Therefore:
#
# - If any critical issue exists, overall health is Critical.
# - If no critical issue exists but a warning exists, overall
#   health is Warning.
# - If no warnings or critical issues exist, overall health is
#   Healthy.
#
# This module does not perform the original diagnostic checks
# itself. Instead, it receives information from the other
# modules and evaluates their results.
#
# The module can also be run independently for testing.
# ============================================================


# ============================================================
# MODULE IMPORTS
# ============================================================
# These functions are imported so that the module can be
# tested independently when system_health.py is run directly.
#
# main.py passes diagnostic information directly into the
# health-check functions when the application is running.
# ============================================================

from disk_usage import get_disk_usage
from firewall_status import get_firewall_status
from security_checks import run_security_checks
from service_status import get_service_status


# ============================================================
# CHECK DISK HEALTH
# ============================================================
# Evaluates disk usage for each detected drive.
#
# Usage thresholds:
#
#     0% - 79%:
#         Healthy
#
#     80% - 89%:
#         Warning
#
#     90% and above:
#         Critical
#
# The function returns a list because a computer may contain
# multiple drives or mount points.
# ============================================================

def check_disk_health(disk_information):

    disk_health = []


    for drive in disk_information:

        try:

            usage = drive["Usage"]


            # ------------------------------------------------
            # CRITICAL DISK USAGE
            # ------------------------------------------------

            if usage >= 90:

                status = "Critical"


            # ------------------------------------------------
            # WARNING DISK USAGE
            # ------------------------------------------------

            elif usage >= 80:

                status = "Warning"


            # ------------------------------------------------
            # HEALTHY DISK USAGE
            # ------------------------------------------------

            else:

                status = "Healthy"


            disk_health.append({

                "Mount Point": drive["Mount Point"],

                "Usage": usage,

                "Status": status

            })


        except (
            KeyError,
            TypeError,
            ValueError
        ):

            # ------------------------------------------------
            # Invalid disk information should not stop the
            # entire health check.
            # ------------------------------------------------

            continue


    return disk_health


# ============================================================
# CHECK FIREWALL HEALTH
# ============================================================
# Evaluates the firewall status returned by firewall_status.py.
#
# Expected healthy values include:
#
#     On
#     Active
#
# Anything else is treated as Critical.
#
# This is intentionally conservative because a firewall that
# cannot be confirmed as active should not be considered
# healthy.
# ============================================================

def check_firewall_health(firewall_information):

    firewall_health = {}


    if not isinstance(
        firewall_information,
        dict
    ):

        return firewall_health


    for profile, status in firewall_information.items():

        try:

            if status.lower() in [
                "on",
                "active"
            ]:

                firewall_health[
                    profile
                ] = "Healthy"


            else:

                firewall_health[
                    profile
                ] = "Critical"


        except (
            AttributeError,
            TypeError
        ):

            firewall_health[
                profile
            ] = "Critical"


    return firewall_health


# ============================================================
# CHECK SECURITY HEALTH
# ============================================================
# Evaluates security-related information.
#
# The function checks:
#
# 1. Administrator / Root privileges
# 2. Network-exposed listening ports
#
# Administrator/root privileges:
#
#     Not elevated:
#         Healthy
#
#     Elevated:
#         Warning
#
# Listening ports:
#
#     No network-exposed ports:
#         Healthy
#
#     One or more network-exposed ports:
#         Warning
#
# Localhost-only services are not counted as network-exposed.
# ============================================================

def check_security_health(security_information):

    security_health = {}


    # ========================================================
    # ADMINISTRATOR / ROOT PRIVILEGES
    # ========================================================

    if (
        "Administrator Privileges"
        in security_information
    ):

        if (
            security_information[
                "Administrator Privileges"
            ]
            == "No"
        ):

            security_health[
                "Administrator Privileges"
            ] = "Healthy"


        else:

            security_health[
                "Administrator Privileges"
            ] = "Warning"


    elif (
        "Root Privileges"
        in security_information
    ):

        if (
            security_information[
                "Root Privileges"
            ]
            == "No"
        ):

            security_health[
                "Root Privileges"
            ] = "Healthy"


        else:

            security_health[
                "Root Privileges"
            ] = "Warning"


    # ========================================================
    # LISTENING PORTS
    # ========================================================

    listening_ports = security_information.get(
        "Listening Ports",
        []
    )


    network_exposed = 0


    # --------------------------------------------------------
    # Handle unexpected error strings returned by the security
    # module.
    # --------------------------------------------------------

    if isinstance(
        listening_ports,
        list
    ):

        for port in listening_ports:

            if not isinstance(
                port,
                dict
            ):

                continue


            if (
                port.get("Exposure")
                == "Network"
            ):

                network_exposed += 1


    # ========================================================
    # DETERMINE NETWORK EXPOSURE HEALTH
    # ========================================================

    if network_exposed == 0:

        security_health[
            "Network Exposed Ports"
        ] = "Healthy"


    else:

        security_health[
            "Network Exposed Ports"
        ] = (
            f"Warning - "
            f"{network_exposed} exposed"
        )


    return security_health


# ============================================================
# CHECK SERVICE HEALTH
# ============================================================
# Evaluates the status of important operating-system services.
#
# Running:
#
#     Healthy
#
# Stopped:
#
#     Warning
#
# Other statuses are returned unchanged so that information
# such as "Command Unavailable" or "Not Found" is not hidden.
# ============================================================

def check_service_health(service_information):

    service_health = {}


    services = service_information.get(
        "Services",
        {}
    )


    if not isinstance(
        services,
        dict
    ):

        return service_health


    for service, status in services.items():

        if status == "Running":

            service_health[
                service
            ] = "Healthy"


        elif status == "Stopped":

            service_health[
                service
            ] = "Warning"


        else:

            service_health[
                service
            ] = status


    return service_health


# ============================================================
# CALCULATE OVERALL SYSTEM HEALTH
# ============================================================
# Combines all health categories into one overall status.
#
# Priority:
#
#     Critical > Warning > Healthy
#
# A status beginning with "Warning" is treated as a Warning.
#
# This is necessary because security health can contain values
# such as:
#
#     Warning - 27 exposed
# ============================================================

def calculate_overall_health(
    disk_health,
    firewall_health,
    security_health,
    service_health
):

    statuses = []


    # ========================================================
    # DISK HEALTH
    # ========================================================

    if isinstance(
        disk_health,
        list
    ):

        for drive in disk_health:

            if isinstance(
                drive,
                dict
            ):

                status = drive.get(
                    "Status"
                )

                if status:

                    statuses.append(
                        status
                    )


    # ========================================================
    # FIREWALL HEALTH
    # ========================================================

    if isinstance(
        firewall_health,
        dict
    ):

        for status in firewall_health.values():

            statuses.append(
                status
            )


    # ========================================================
    # SECURITY HEALTH
    # ========================================================

    if isinstance(
        security_health,
        dict
    ):

        for status in security_health.values():

            if (
                isinstance(status, str)
                and status.startswith("Warning")
            ):

                statuses.append(
                    "Warning"
                )

            else:

                statuses.append(
                    status
                )


    # ========================================================
    # SERVICE HEALTH
    # ========================================================

    if isinstance(
        service_health,
        dict
    ):

        for status in service_health.values():

            statuses.append(
                status
            )


    # ========================================================
    # DETERMINE OVERALL STATUS
    # ========================================================

    if "Critical" in statuses:

        return "Critical"


    elif "Warning" in statuses:

        return "Warning"


    else:

        return "Healthy"


# ============================================================
# STANDALONE TEST
# ============================================================
# This section allows system_health.py to be tested without
# running the complete TechAssist application.
#
# It collects fresh diagnostic information from the other
# modules and evaluates each category.
# ============================================================

if __name__ == "__main__":

    # ========================================================
    # DISK HEALTH
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
    # FIREWALL HEALTH
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
    # SECURITY HEALTH
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
    # SERVICE HEALTH
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
    # OVERALL SYSTEM HEALTH
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