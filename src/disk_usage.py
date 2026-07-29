import psutil

def get_disk_usage():
    disk_information = []
    partitions = psutil.disk_partitions()

    for partition in partitions:

        try:    
            usage = psutil.disk_usage(partition.mountpoint)

        except PermissionError:
            continue

        total_gb = round(usage.total / (1024 ** 3), 2)
        used_gb = round(usage.used / (1024 ** 3), 2)
        free_gb = round(usage.free / (1024 ** 3), 2)

        disk_information.append({
            "Drive": partition.device,
            "Total Space": f"{total_gb} GB",
            "Used Space": f"{used_gb} GB",
            "Free Space": f"{free_gb} GB",
            "Usage": f"{usage.percent} %"
        })

    return disk_information