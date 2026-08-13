# ============================================================
# FIREWALL STATUS MODULE
# ============================================================
# This module checks the status of the operating system's
# built-in firewall.
#
# Different operating systems use different firewall
# management tools, so platform-specific commands are used:
#
# Windows:
#   netsh advfirewall
#
# Linux:
#   UFW (Uncomplicated Firewall)
#
# macOS:
#   socketfilterfw
#
# The results are returned as a dictionary so that they can be
# displayed by main.py and included in diagnostic reports.
# ============================================================


# ============================================================
# MODULE IMPORTS
# ============================================================

# platform is used to identify which operating system the
# toolkit is currently running on.
import platform


# subprocess allows Python to execute operating-system commands
# and capture their output.
import subprocess


# ============================================================
# GET FIREWALL STATUS
# ============================================================
# Detects the operating system and checks the status of its
# firewall.
# ============================================================

def get_firewall_status():

    # Identify the operating system.
    #
    # Expected values include:
    #
    # Windows
    # Linux
    # Darwin (macOS)
    operating_system = platform.system()


    # ========================================================
    # WINDOWS FIREWALL
    # ========================================================
    # Windows provides firewall configuration information
    # through the netsh command.
    #
    # The "allprofiles" option retrieves information for:
    #
    # - Domain
    # - Private
    # - Public
    #
    # firewall profiles.
    # ========================================================

    if operating_system == "Windows":

        result = subprocess.run(
            [
                "netsh",
                "advfirewall",
                "show",
                "allprofiles"
            ],
            capture_output=True,
            text=True
        )


        # Store the command output so it can be analysed.
        firewall_output = result.stdout


        # Dictionary used to store the state of each Windows
        # firewall profile.
        firewall_status = {}


        # Keeps track of which firewall profile is currently
        # being processed while reading the command output.
        current_profile = None


        # Split the command output into individual lines so
        # each line can be examined.
        lines = firewall_output.splitlines()


        # ----------------------------------------------------
        # PROCESS WINDOWS FIREWALL PROFILES
        # ----------------------------------------------------

        for line in lines:

            # Identify the Domain firewall profile.
            if "Domain Profile Settings" in line:

                current_profile = "Domain"


            # Identify the Private firewall profile.
            elif "Private Profile Settings" in line:

                current_profile = "Private"


            # Identify the Public firewall profile.
            elif "Public Profile Settings" in line:

                current_profile = "Public"


            # ------------------------------------------------
            # FIREWALL STATE
            # ------------------------------------------------
            # Once a profile has been identified, a line
            # containing "State" provides its current status.
            #
            # The final item on the line contains the state,
            # such as ON or OFF.
            # ------------------------------------------------

            elif "State" in line:

                firewall_status[current_profile] = (
                    line.split()[-1]
                )


    # ========================================================
    # LINUX FIREWALL
    # ========================================================
    # On Linux, the toolkit checks UFW, the Uncomplicated
    # Firewall command-line interface.
    #
    # "ufw status" reports whether the firewall is active.
    # ========================================================

    elif operating_system == "Linux":

        result = subprocess.run(
            ["ufw", "status"],
            capture_output=True,
            text=True
        )


        # Store the command output for analysis.
        firewall_output = result.stdout


        # UFW reports an enabled firewall using:
        #
        # Status: active
        #
        # If this text is present, the firewall is considered
        # active.
        if "Status: active" in firewall_output:

            return {
                "Firewall": "Active"
            }


        # If "Status: active" is not present, the toolkit
        # reports the firewall as inactive.
        else:

            return {
                "Firewall": "Inactive"
            }


    # ========================================================
    # macOS FIREWALL
    # ========================================================
    # macOS uses Apple's Application Firewall.
    #
    # The socketfilterfw utility can be used to query the
    # firewall's global state.
    #
    # This section requires testing on a physical macOS system
    # to confirm the output format across supported versions.
    # ========================================================

    elif operating_system == "Darwin":

        result = subprocess.run(
            [
                "/usr/libexec/ApplicationFirewall/socketfilterfw",
                "--getglobalstate"
            ],
            capture_output=True,
            text=True
        )


        # Combine standard output and error output because
        # socketfilterfw may provide status information through
        # either stream depending on the system.
        firewall_output = result.stdout + result.stderr


        # Look for the word "enabled" in the command output.
        if "enabled" in firewall_output.lower():

            return {
                "Firewall": "Active"
            }


        # If "enabled" is not found, report the firewall as
        # inactive.
        else:

            return {
                "Firewall": "Inactive"
            }


    # ========================================================
    # RETURN WINDOWS FIREWALL RESULTS
    # ========================================================
    # Windows stores the results for each firewall profile in
    # firewall_status.
    #
    # Linux and macOS return their results earlier because
    # their firewall output is represented as a single status.
    # ========================================================

    return firewall_status

