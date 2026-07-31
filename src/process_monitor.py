import psutil

def get_processes():

    process_information = []


    for process in psutil.process_iter({'pid', 'name','status', 'memory_info'}):

        try:

            memory_mb = round(
                process.info['memory_info'].rss / (1024 ** 2),
                2
            )

            cpu_percent = process.cpu_percent(interval=None)

            process_information.append({
                "Name": process.info['name'],
                "PID": process.info['pid'],
                "Status": process.info['status'],
                "CPU Usage (%)": cpu_percent,
                "Memory Usage (MB)": memory_mb
            })

        except (psutil.NoSuchProcess,
                psutil.AccessDenied,
                psutil.ZombieProcess):
            continue

    process_information.sort(
        key=lambda x: x["Memory Usage (MB)"],
        reverse=True
        )

    return process_information[:10]  # Return top 10 processes by memory usage