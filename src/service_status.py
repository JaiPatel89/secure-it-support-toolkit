# ============================================================
# SERVICE STATUS MODULE
# ============================================================
# This module checks the status of important operating-system
# services.
#
# The services checked depend on the operating system.
#
# Windows:
#     - Windows Update
#     - DNS Client
#     - Print Spooler
#     - Microsoft Defender
#
# Linux:
#     - SSH
#     - Cron
#
# macOS:
#     - SSH
#
# The module standardizes service states so that different
# operating systems can return consistent results.
#
# For example:
#
#     running  -> Running
#     active   -> Running
#     stopped  -> Stopped
#     inactive -> Stopped
#
# The results are returned as a dictionary so that they can be
# displayed by main.py, used by system_health.py and included
# in the diagnostic report.
#
# Error handling is included because:
#
# - A service may not exist.
# - A command may not be available.
# - A service may change state while being checked.
# - The command may fail or time out.
# ============================================================


# ============================================================
# MODULE IMPORTS
# ============================================================
# The following modules provide the functionality required to
# identify the operating system and execute service-management
# commands.
# ============================================================


# platform identifies the operating system.
import platform


# subprocess allows the toolkit to execute operating-system
# service commands such as PowerShell, systemctl and launchctl.
import subprocess


# ============================================================
# RUN COMMAND
# ============================================================
# Executes an operating-system command safely.
#
# Returning None when the command cannot be executed allows the
# calling function to handle the problem without crashing.
# ============================================================

def run_command(command):

    try:

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=10
        )

        return result


    # --------------------------------------------------------
    # COMMAND NOT FOUND
    # --------------------------------------------------------
    # Raised when the requested executable is unavailable.
    # --------------------------------------------------------

    except FileNotFoundError:

        return None


    # --------------------------------------------------------
    # COMMAND TIMEOUT
    # --------------------------------------------------------
    # Prevents a service command from hanging indefinitely.
    # --------------------------------------------------------

    except subprocess.TimeoutExpired:

        return None


    # --------------------------------------------------------
    # GENERAL ERROR
    # --------------------------------------------------------

    except Exception:

        return None


# ============================================================
# STANDARDIZE STATUS
# ============================================================
# Converts different service status values into consistent
# output used throughout TechAssist.
#
# Running states:
#
#     running
#     active
#
# become:
#
#     Running
#
# Stopped states:
#
#     stopped
#     inactive
#     dead
#     failed
#
# become:
#
#     Stopped
# ============================================================

def standardize_status(status):

    status = status.strip().lower()


    if status in [
        "running",
        "active"
    ]:

        return "Running"


    elif status in [
        "stopped",
        "inactive",
        "dead",
        "failed"
    ]:

        return "Stopped"


    else:

        return status.capitalize()


# ============================================================
# GET SERVICE STATUS
# ============================================================
# Retrieves service information for the current operating
# system.
# ============================================================

def get_service_status():

    try:

        operating_system = platform.system()

    except Exception:

        operating_system = "Unknown"


    # Dictionary containing the results for each service.
    service_results = {}


    # ========================================================
    # WINDOWS SERVICES
    # ========================================================
    # Windows services are queried using PowerShell's
    # Get-Service command.
    #
    # Service names are different from their display names,
    # so both are stored in the dictionary.
    # ========================================================

    if operating_system == "Windows":

        services = {

            "Windows Update": "wuauserv",

            "DNS Client": "Dnscache",

            "Print Spooler": "Spooler",

            "Microsoft Defender": "WinDefend"

        }


        for display_name, service_name in services.items():

            result = run_command(
                [
                    "powershell",
                    "-Command",
                    (
                        f"(Get-Service "
                        f"-Name '{service_name}' "
                        f"-ErrorAction SilentlyContinue)"
                        f".Status"
                    )
                ]
            )


            # ------------------------------------------------
            # COMMAND UNAVAILABLE
            # ------------------------------------------------

            if result is None:

                service_results[
                    display_name
                ] = "Command Unavailable"

                continue


            # ------------------------------------------------
            # CHECK COMMAND RESULT
            # ------------------------------------------------

            status = result.stdout.strip()


            if status:

                service_results[
                    display_name
                ] = standardize_status(status)


            else:

                service_results[
                    display_name
                ] = "Not Found"


    # ========================================================
    # LINUX SERVICES
    # ========================================================
    # Linux services are queried using systemctl.
    #
    # is-active returns states such as:
    #
    #     active
    #     inactive
    #     failed
    # ========================================================

    elif operating_system == "Linux":

        services = {

            "SSH": "ssh",

            "Cron": "cron"

        }


        for display_name, service_name in services.items():

            result = run_command(
                [
                    "systemctl",
                    "is-active",
                    service_name
                ]
            )


            if result is None:

                service_results[
                    display_name
                ] = "Command Unavailable"

                continue


            status = result.stdout.strip()


            if status:

                service_results[
                    display_name
                ] = standardize_status(status)


            else:

                service_results[
                    display_name
                ] = "Not Found"


    # ========================================================
    # macOS SERVICES
    # ========================================================
    # macOS uses launchctl to manage system services.
    #
    # The SSH daemon is identified by:
    #
    #     com.openssh.sshd
    # ========================================================

    elif operating_system == "Darwin":

        services = {

            "SSH": "com.openssh.sshd"

        }


        for display_name, service_name in services.items():

            result = run_command(
                [
                    "launchctl",
                    "list",
                    service_name
                ]
            )


            if result is None:

                service_results[
                    display_name
                ] = "Command Unavailable"


            elif result.returncode == 0:

                service_results[
                    display_name
                ] = "Running"


            else:

                service_results[
                    display_name
                ] = "Stopped"


    # ========================================================
    # UNSUPPORTED OPERATING SYSTEM
    # ========================================================

    else:

        service_results[
            "Services"
        ] = "Unsupported Operating System"


    # ========================================================
    # RETURN SERVICE INFORMATION
    # ========================================================
    # Both the operating system and service results are
    # returned so that main.py can display them correctly.
    # ========================================================

    return {

        "Operating System": operating_system,

        "Services": service_results

    }


# ============================================================
# STANDALONE TEST
# ============================================================
# Allows service_status.py to be tested independently from
# main.py.
#
# This section only runs when the file itself is executed.
# ============================================================

if __name__ == "__main__":

    results = get_service_status()


    print("SERVICE STATUS")
    print("--------------")


    print(
        f"Operating System: "
        f"{results['Operating System']}"
    )


    print()


    for service, status in results["Services"].items():

        print(
            f"{service}: {status}"
        )