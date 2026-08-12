from disk_usage import get_disk_usage
from firewall_status import get_firewall_status
from security_checks import run_security_checks
from service_status import get_service_status


def check_disk_health(disk_information):

    disk_health = []

    for drive in disk_information:

        usage = drive["Usage"]

        if usage >= 90:
            status = "Critical"

        elif usage >= 80:
            status = "Warning"

        else:
            status = "Healthy"

        disk_health.append({
            "Mount Point": drive["Mount Point"],
            "Usage": usage,
            "Status": status
        })

    return disk_health


def check_firewall_health(firewall_information):

    firewall_health = {}

    for profile, status in firewall_information.items():

        if status.lower() in ["on", "active"]:
            firewall_health[profile] = "Healthy"

        else:
            firewall_health[profile] = "Critical"

    return firewall_health


def check_security_health(security_information):

    security_health = {}

    # Administrator / Root privileges

    if "Administrator Privileges" in security_information:

        if security_information["Administrator Privileges"] == "No":
            security_health["Administrator Privileges"] = "Healthy"

        else:
            security_health["Administrator Privileges"] = "Warning"

    elif "Root Privileges" in security_information:

        if security_information["Root Privileges"] == "No":
            security_health["Root Privileges"] = "Healthy"

        else:
            security_health["Root Privileges"] = "Warning"

    # Listening ports

    listening_ports = security_information.get("Listening Ports", [])

    network_exposed = 0

    for port in listening_ports:

        if port.get("Exposure") == "Network":
            network_exposed += 1

    if network_exposed == 0:
        security_health["Network Exposed Ports"] = "Healthy"

    else:
        security_health["Network Exposed Ports"] = (
            f"Warning - {network_exposed} exposed"
        )

    return security_health


def check_service_health(service_information):

    service_health = {}

    services = service_information.get("Services", {})

    for service, status in services.items():

        if status == "Running":
            service_health[service] = "Healthy"

        elif status == "Stopped":
            service_health[service] = "Warning"

        else:
            service_health[service] = status

    return service_health


def calculate_overall_health(
    disk_health,
    firewall_health,
    security_health,
    service_health
):

    statuses = []

    # Disk Health

    for drive in disk_health:
        statuses.append(drive["Status"])

    # Firewall Health

    for status in firewall_health.values():
        statuses.append(status)

    # Security Health

    for status in security_health.values():

        if status.startswith("Warning"):
            statuses.append("Warning")

        else:
            statuses.append(status)

    # Service Health

    for status in service_health.values():
        statuses.append(status)

    # Determine overall status

    if "Critical" in statuses:
        return "Critical"

    elif "Warning" in statuses:
        return "Warning"

    else:
        return "Healthy"


if __name__ == "__main__":

    # Disk Health

    disk_information = get_disk_usage()

    disk_results = check_disk_health(disk_information)

    print("DISK HEALTH")
    print("-----------")

    for drive in disk_results:

        print(f"Mount Point: {drive['Mount Point']}")
        print(f"Usage: {drive['Usage']} %")
        print(f"Status: {drive['Status']}")
        print()


    # Firewall Health

    firewall_information = get_firewall_status()

    firewall_results = check_firewall_health(firewall_information)

    print("FIREWALL HEALTH")
    print("---------------")

    for profile, status in firewall_results.items():

        print(f"{profile}: {status}")


    # Security Health

    security_information = run_security_checks()

    security_results = check_security_health(security_information)

    print()
    print("SECURITY HEALTH")
    print("---------------")

    for check, status in security_results.items():

        print(f"{check}: {status}")


    # Service Health

    service_information = get_service_status()

    service_results = check_service_health(service_information)

    print()
    print("SERVICE HEALTH")
    print("--------------")

    for service, status in service_results.items():

        print(f"{service}: {status}")


    # Overall System Health

    overall_status = calculate_overall_health(
        disk_results,
        firewall_results,
        security_results,
        service_results
    )

    print()
    print("OVERALL SYSTEM HEALTH")
    print("---------------------")
    print(f"Status: {overall_status}")