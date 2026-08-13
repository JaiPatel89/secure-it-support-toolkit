# ============================================================
# SERVICE STATUS MODULE
# ============================================================
# This module checks the status of important operating system
# services.
#
# Different operating systems manage services differently:
#
# Windows:
#   PowerShell / Windows Services
#
# Linux:
#   systemctl
#
# macOS:
#   launchctl
#
# The module standardizes the different status values returned
# by these operating systems so the rest of the toolkit can
# work with a consistent set of results.
#
# The results are returned as a dictionary containing:
#
# - Operating system
# - Service names
# - Service status
# ============================================================


# ============================================================
# MODULE IMPORTS
# ============================================================

# platform is used to identify the operating system.
import platform


# subprocess allows Python to execute operating-system
# commands and capture their output.
import subprocess


# ============================================================
# RUN COMMAND
# ============================================================
# Executes an operating-system command and returns the result.
#
# This helper function keeps command execution in one place
# and provides basic error handling.
# ============================================================

def run_command(command):

    try:

        # Execute the supplied command.
        #
        # capture_output=True stores stdout and stderr so they
        # can be examined by the toolkit.
        #
        # text=True means the output is returned as strings
        # rather than raw bytes.
        result = subprocess.run(
            command,
            capture_output=True,
            text=True
        )


        # Return the completed subprocess result.
        return result


    # FileNotFoundError occurs when the required command is not
    # available on the operating system.
    #
    # For example, a Linux system may not have the Windows
    # PowerShell service commands available.
    except FileNotFoundError:

        return None


    # Catch any other unexpected command execution errors.
    except Exception as error:

        print(f"Command error: {error}")

        return None


# ============================================================
# STANDARDIZE SERVICE STATUS
# ============================================================
# Different operating systems use different terminology for
# service states.
#
# For example:
#
# Windows:
#   Running
#   Stopped
#
# Linux:
#   active
#   inactive
#   failed
#   dead
#
# This function converts those different values into a common
# format that the rest of the toolkit can understand.
# ============================================================

def standardize_status(status):

    # Remove unnecessary whitespace and convert the status to
    # lowercase so comparisons are consistent.
    status = status.strip().lower()


    # Both "running" and "active" indicate that the service is
    # currently operational.
    if status in ["running", "active"]:

        return "Running"


    # These statuses indicate that the service is not currently
    # operational.
    elif status in [
        "stopped",
        "inactive",
        "dead",
        "failed"
    ]:

        return "Stopped"


    # If an unfamiliar status is returned, preserve the value
    # but capitalize the first character.
    else:

        return status.capitalize()


# ============================================================
# GET SERVICE STATUS
# ============================================================
# Detects the operating system and checks a predefined set of
# important services.
# ============================================================

def get_service_status():

    # Identify the operating system.
    #
    # Windows returns "Windows"
    # Linux returns "Linux"
    # macOS returns "Darwin"
    operating_system = platform.system()


    # Dictionary used to store the service results.
    service_results = {}


    # ========================================================
    # WINDOWS SERVICES
    # ========================================================
    # Windows services are queried using PowerShell.
    #
    # The dictionary maps a user-friendly display name to the
    # actual Windows service name.
    # ========================================================

    if operating_system == "Windows":

        services = {

            "Windows Update": "wuauserv",

            "DNS Client": "Dnscache",

            "Print Spooler": "Spooler",

            "Microsoft Defender": "WinDefend"
        }


        # Check each Windows service.
        for display_name, service_name in services.items():


            # PowerShell is used to retrieve the service status.
            #
            # -Name identifies the Windows service.
            #
            # -ErrorAction SilentlyContinue prevents PowerShell
            # from displaying an error if the service cannot be
            # found.
            result = run_command(
                [
                    "powershell",
                    "-Command",
                    f"(Get-Service -Name '{service_name}' "
                    f"-ErrorAction SilentlyContinue).Status"
                ]
            )


            # If PowerShell could not be executed, report that
            # the command is unavailable.
            if result is None:

                service_results[
                    display_name
                ] = "Command Unavailable"


            else:

                # Retrieve the service status from stdout.
                status = result.stdout.strip()


                # If a status was returned, standardize it before
                # storing it.
                if status:

                    service_results[
                        display_name
                    ] = standardize_status(status)


                # No status usually means the requested service
                # could not be found.
                else:

                    service_results[
                        display_name
                    ] = "Not Found"


    # ========================================================
    # LINUX SERVICES
    # ========================================================
    # Linux systems using systemd can query services with
    # systemctl.
    #
    # systemctl is-active returns values such as:
    #
    # active
    # inactive
    # failed
    # ========================================================

    elif operating_system == "Linux":

        services = {

            "SSH": "ssh",

            "Cron": "cron"
        }


        # Check each Linux service.
        for display_name, service_name in services.items():

            result = run_command(
                [
                    "systemctl",
                    "is-active",
                    service_name
                ]
            )


            # If systemctl is unavailable, report that the
            # command could not be executed.
            if result is None:

                service_results[
                    display_name
                ] = "Command Unavailable"


            else:

                # Retrieve the service status.
                status = result.stdout.strip()


                # Standardize the status if a value was returned.
                if status:

                    service_results[
                        display_name
                    ] = standardize_status(status)


                # No output indicates that the service could not
                # be identified.
                else:

                    service_results[
                        display_name
                    ] = "Not Found"


    # ========================================================
    # macOS SERVICES
    # ========================================================
    # macOS uses launchd to manage system services.
    #
    # launchctl is used to query the OpenSSH service.
    # ========================================================

    elif operating_system == "Darwin":

        services = {

            "SSH": "com.openssh.sshd"
        }


        # Check each macOS service.
        for display_name, service_name in services.items():

            result = run_command(
                [
                    "launchctl",
                    "list",
                    service_name
                ]
            )


            # If launchctl cannot be executed, report that the
            # command is unavailable.
            if result is None:

                service_results[
                    display_name
                ] = "Command Unavailable"


            # A return code of 0 indicates that launchctl
            # successfully found the requested service.
            elif result.returncode == 0:

                service_results[
                    display_name
                ] = "Running"


            # A non-zero return code indicates that the service
            # was not found or is not currently loaded.
            else:

                service_results[
                    display_name
                ] = "Stopped"


    # ========================================================
    # RETURN SERVICE INFORMATION
    # ========================================================
    # Return both the operating system and the collected
    # service information.
    #
    # Keeping the operating system in the result allows
    # main.py and the report generator to clearly identify
    # which platform was checked.
    # ========================================================

    return {

        "Operating System": operating_system,

        "Services": service_results
    }


# ============================================================
# STANDALONE MODULE TEST
# ============================================================
# This section only runs when service_status.py itself is
# executed directly.
#
# It does not run when the module is imported by main.py.
#
# This makes it possible to test the module independently
# without launching the entire toolkit.
# ============================================================

if __name__ == "__main__":

    results = get_service_status()


    print(
        f"Operating System: "
        f"{results['Operating System']}"
    )


    for service, status in results["Services"].items():

        print(
            f"{service}: {status}"
        )