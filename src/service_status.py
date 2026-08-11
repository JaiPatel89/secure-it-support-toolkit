import platform
import subprocess

def run_command(command):
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True
        )

        return result

    except FileNotFoundError:
        return None

    except Exception as error:
        print(f"Command error: {error}")
        return None


def standardize_status(status):
    status = status.strip().lower()

    if status in ["running", "active"]:
        return "Running"

    elif status in ["stopped", "inactive", "dead", "failed"]:
        return "Stopped"

    else:
        return status.capitalize()


def get_service_status():
    operating_system = platform.system()

    service_results = {}

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
                    f"(Get-Service -Name '{service_name}' "
                    f"-ErrorAction SilentlyContinue).Status"
                ]
            )

            if result is None:
                service_results[display_name] = "Command Unavailable"

            else:
                status = result.stdout.strip()

                if status:
                    service_results[display_name] = standardize_status(status)
                else:
                    service_results[display_name] = "Not Found"

    elif operating_system == "Linux":

        services = {
            "SSH": "ssh",
            "Cron": "cron"
        }

        for display_name, service_name in services.items():
            result = run_command(
                ["systemctl", "is-active", service_name]
            )

            if result is None:
                service_results[display_name] = "Command Unavailable"

            else:
                status = result.stdout.strip()

                if status:
                    service_results[display_name] = standardize_status(status)
                else:
                    service_results[display_name] = "Not Found"

    elif operating_system == "Darwin":

        services = {
            "SSH": "com.openssh.sshd"
        }

        for display_name, service_name in services.items():

            result = run_command(
                ["launchctl", "list", service_name]
            )

            if result is None:
                service_results[display_name] = "Command Unavailable"

            elif result.returncode == 0:
                service_results[display_name] = "Running"

            else:
                service_results[display_name] = "Stopped"

    return {
        "Operating System": operating_system,
        "Services": service_results
    }


if __name__ == "__main__":
    results = get_service_status()

    print(f"Operating System: {results['Operating System']}")

    for service, status in results["Services"].items():
        print(f"{service}: {status}")