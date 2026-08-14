# ============================================================
# FIREWALL STATUS MODULE
# ============================================================
# This module checks whether the operating system firewall is
# enabled.
#
# Different operating systems use different firewall tools:
#
# Windows:
#     netsh
#
# Linux:
#     UFW (Uncomplicated Firewall)
#
# macOS:
#     socketfilterfw
#
# The function returns firewall information as a dictionary
# so that it can be displayed by main.py and included in the
# diagnostic report.
#
# Error handling is used when executing firewall commands so
# that a missing command, inaccessible firewall configuration
# or unexpected command failure does not cause the entire
# toolkit to stop.
# ============================================================


# ============================================================
# MODULE IMPORTS
# ============================================================
# The following modules provide the functionality required to
# identify the operating system and execute firewall commands.
# ============================================================


# platform identifies which operating system is being used.
# This allows the appropriate firewall command to be selected.
import platform


# subprocess allows the toolkit to execute operating-system
# commands such as netsh, ufw and socketfilterfw.
import subprocess


# ============================================================
# GET FIREWALL STATUS
# ============================================================
# Determines the firewall status for the operating system.
#
# Windows returns the status of the Domain, Private and Public
# firewall profiles.
#
# Linux and macOS return the overall firewall status.
# ============================================================

def get_firewall_status():

    operating_system = platform.system()


    # Dictionary used to store Windows firewall profile status.
    firewall_status = {}


    # ========================================================
    # WINDOWS FIREWALL
    # ========================================================
    # Windows provides firewall information through the netsh
    # command.
    #
    # The command checks all three Windows Firewall profiles:
    #
    # - Domain
    # - Private
    # - Public
    # ========================================================

    if operating_system == "Windows":

        try:

            result = subprocess.run(
                [
                    "netsh",
                    "advfirewall",
                    "show",
                    "allprofiles"
                ],
                capture_output=True,
                text=True,
                timeout=10
            )


        # ----------------------------------------------------
        # ERROR HANDLING
        # ----------------------------------------------------
        # FileNotFoundError means the netsh command could not
        # be located.
        # ----------------------------------------------------

        except FileNotFoundError:

            return {
                "Firewall": "Command Unavailable"
            }


        # ----------------------------------------------------
        # TIMEOUT HANDLING
        # ----------------------------------------------------
        # Prevents the toolkit from waiting indefinitely for
        # the firewall command to complete.
        # ----------------------------------------------------

        except subprocess.TimeoutExpired:

            return {
                "Firewall": "Command Timed Out"
            }


        # ----------------------------------------------------
        # GENERAL COMMAND ERROR
        # ----------------------------------------------------

        except Exception:

            return {
                "Firewall": "Unable to determine"
            }


        # ====================================================
        # CHECK COMMAND RESULT
        # ====================================================
        # If the command failed, return a descriptive status
        # instead of attempting to process incomplete output.
        # ====================================================

        if result.returncode != 0:

            return {
                "Firewall": "Unable to determine"
            }


        firewall_output = result.stdout


        # ====================================================
        # PROCESS WINDOWS PROFILES
        # ====================================================

        current_profile = None

        lines = firewall_output.splitlines()


        for line in lines:

            if "Domain Profile Settings" in line:

                current_profile = "Domain"


            elif "Private Profile Settings" in line:

                current_profile = "Private"


            elif "Public Profile Settings" in line:

                current_profile = "Public"


            elif (
                "State" in line
                and current_profile is not None
            ):

                firewall_status[current_profile] = (
                    line.split()[-1]
                )


        # ====================================================
        # CHECK WHETHER PROFILE INFORMATION WAS FOUND
        # ====================================================
        # If no profiles were successfully identified, return
        # a descriptive error rather than an empty dictionary.
        # ====================================================

        if not firewall_status:

            return {
                "Firewall": "Unable to determine"
            }


    # ========================================================
    # LINUX FIREWALL
    # ========================================================
    # Linux systems commonly use UFW to manage firewall rules.
    #
    # The command:
    #
    #     ufw status
    #
    # is used to determine whether the firewall is active.
    # ========================================================

    elif operating_system == "Linux":

        try:

            result = subprocess.run(
                ["ufw", "status"],
                capture_output=True,
                text=True,
                timeout=10
            )


        except FileNotFoundError:

            return {
                "Firewall": "Command Unavailable"
            }


        except subprocess.TimeoutExpired:

            return {
                "Firewall": "Command Timed Out"
            }


        except Exception:

            return {
                "Firewall": "Unable to determine"
            }


        firewall_output = (
            result.stdout + result.stderr
        )


        if "Status: active" in firewall_output:

            return {
                "Firewall": "Active"
            }

        elif "Status: inactive" in firewall_output:

            return {
                "Firewall": "Inactive"
            }

        else:

            return {
                "Firewall": "Unable to determine"
            }


    # ========================================================
    # macOS FIREWALL
    # ========================================================
    # macOS provides Application Firewall information through:
    #
    # /usr/libexec/ApplicationFirewall/socketfilterfw
    #
    # The --getglobalstate option reports whether the firewall
    # is enabled.
    # ========================================================

    elif operating_system == "Darwin":

        try:

            result = subprocess.run(
                [
                    "/usr/libexec/ApplicationFirewall/"
                    "socketfilterfw",
                    "--getglobalstate"
                ],
                capture_output=True,
                text=True,
                timeout=10
            )


        except FileNotFoundError:

            return {
                "Firewall": "Command Unavailable"
            }


        except subprocess.TimeoutExpired:

            return {
                "Firewall": "Command Timed Out"
            }


        except Exception:

            return {
                "Firewall": "Unable to determine"
            }


        firewall_output = (
            result.stdout + result.stderr
        )


        if "enabled" in firewall_output.lower():

            return {
                "Firewall": "Active"
            }

        elif "disabled" in firewall_output.lower():

            return {
                "Firewall": "Inactive"
            }

        else:

            return {
                "Firewall": "Unable to determine"
            }


    # ========================================================
    # UNSUPPORTED OPERATING SYSTEM
    # ========================================================
    # If the operating system is not currently supported,
    # return a descriptive result instead of failing.
    # ========================================================

    else:

        return {
            "Firewall": "Unsupported Operating System"
        }


    # ========================================================
    # RETURN FIREWALL STATUS
    # ========================================================
    # Windows reaches this point after processing the Domain,
    # Private and Public firewall profiles.
    #
    # Linux and macOS return earlier because they use a single
    # overall firewall status.
    # ========================================================

    return firewall_status


# ============================================================
# STANDALONE TEST
# ============================================================
# This allows firewall_status.py to be tested independently
# from the main TechAssist application.
#
# The code below only runs when this file is executed directly.
# It does not run when the module is imported by main.py.
# ============================================================

if __name__ == "__main__":

    firewall_information = get_firewall_status()


    for item, value in firewall_information.items():

        print(f"{item}: {value}")
