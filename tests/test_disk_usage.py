# ============================================================
# DISK USAGE TESTS
# ============================================================
# This module contains automated tests for disk_usage.py.
#
# The tests verify that the disk usage module correctly:
#
# - Detects disk partitions
# - Calculates disk usage
# - Converts storage values to GB
# - Returns the expected information structure
# - Handles permission errors
# - Skips unwanted Linux mount points
#
# The tests use controlled mock data rather than relying on
# the actual computer's disks.
#
# This makes the tests predictable and repeatable.
# ============================================================


# ============================================================
# TEST MODULE PATH
# ============================================================
# The application modules are stored inside the src directory.
#
# Pytest runs from the project root, so src must be added to
# Python's module search path.
# ============================================================

import sys
from pathlib import Path


sys.path.insert(
    0,
    str(
        Path(__file__).resolve().parent.parent / "src"
    )
)


# ============================================================
# MODULE IMPORTS
# ============================================================
# psutil is used by the application and is also used here to
# create controlled disk usage test values.
#
# Simple mock objects are used for partitions because the
# internal psutil partition classes can vary between versions.
# ============================================================

import psutil

from types import SimpleNamespace

from disk_usage import get_disk_usage


# ============================================================
# TEST DISK USAGE
# ============================================================
# Verifies that disk information is correctly collected and
# converted into the expected format.
# ============================================================

def test_disk_usage(monkeypatch):

    # --------------------------------------------------------
    # Create a fake partition.
    # --------------------------------------------------------

    fake_partition = SimpleNamespace(
        device="C:",
        mountpoint="C:\\",
        fstype="NTFS"
    )


    # --------------------------------------------------------
    # Replace psutil.disk_partitions() with controlled test
    # data.
    # --------------------------------------------------------

    monkeypatch.setattr(
        psutil,
        "disk_partitions",
        lambda: [fake_partition]
    )


    # --------------------------------------------------------
    # Create fake disk usage information.
    #
    # 500 GB total
    # 250 GB used
    # 250 GB free
    # 50% usage
    # --------------------------------------------------------

    fake_usage = SimpleNamespace(
        total=500 * (1024 ** 3),
        used=250 * (1024 ** 3),
        free=250 * (1024 ** 3),
        percent=50.0
    )


    # --------------------------------------------------------
    # Replace psutil.disk_usage() with our fake data.
    # --------------------------------------------------------

    monkeypatch.setattr(
        psutil,
        "disk_usage",
        lambda mountpoint: fake_usage
    )


    # --------------------------------------------------------
    # Run the function being tested.
    # --------------------------------------------------------

    result = get_disk_usage()


    # --------------------------------------------------------
    # Verify one drive was returned.
    # --------------------------------------------------------

    assert len(result) == 1


    drive = result[0]


    # --------------------------------------------------------
    # Verify partition information.
    # --------------------------------------------------------

    assert drive["Mount Point"] == "C:\\"
    assert drive["Device"] == "C:"
    assert drive["Filesystem Type"] == "NTFS"


    # --------------------------------------------------------
    # Verify storage calculations.
    # --------------------------------------------------------

    assert drive["Total Space"] == "500.0 GB"
    assert drive["Used Space"] == "250.0 GB"
    assert drive["Free Space"] == "250.0 GB"


    # --------------------------------------------------------
    # Verify usage percentage.
    # --------------------------------------------------------

    assert drive["Usage"] == 50.0


# ============================================================
# TEST MULTIPLE PARTITIONS
# ============================================================
# Verifies that multiple partitions are processed correctly.
# ============================================================

def test_multiple_partitions(monkeypatch):

    partitions = [

        SimpleNamespace(
            device="C:",
            mountpoint="C:\\",
            fstype="NTFS"
        ),

        SimpleNamespace(
            device="D:",
            mountpoint="D:\\",
            fstype="NTFS"
        )

    ]


    monkeypatch.setattr(
        psutil,
        "disk_partitions",
        lambda: partitions
    )


    def fake_disk_usage(mountpoint):

        if mountpoint == "C:\\":

            return SimpleNamespace(
                total=100 * (1024 ** 3),
                used=50 * (1024 ** 3),
                free=50 * (1024 ** 3),
                percent=50.0
            )

        return SimpleNamespace(
            total=200 * (1024 ** 3),
            used=100 * (1024 ** 3),
            free=100 * (1024 ** 3),
            percent=50.0
        )


    monkeypatch.setattr(
        psutil,
        "disk_usage",
        fake_disk_usage
    )


    result = get_disk_usage()


    # --------------------------------------------------------
    # Both partitions should be returned.
    # --------------------------------------------------------

    assert len(result) == 2


    assert result[0]["Mount Point"] == "C:\\"
    assert result[1]["Mount Point"] == "D:\\"


# ============================================================
# TEST PERMISSION ERROR
# ============================================================
# Verifies that the function skips a partition when
# psutil.disk_usage() raises PermissionError.
# ============================================================

def test_permission_error(monkeypatch):

    fake_partition = SimpleNamespace(
        device="C:",
        mountpoint="C:\\",
        fstype="NTFS"
    )


    monkeypatch.setattr(
        psutil,
        "disk_partitions",
        lambda: [fake_partition]
    )


    def raise_permission_error(mountpoint):

        raise PermissionError(
            "Access denied"
        )


    monkeypatch.setattr(
        psutil,
        "disk_usage",
        raise_permission_error
    )


    result = get_disk_usage()


    # --------------------------------------------------------
    # The inaccessible partition should be skipped.
    # --------------------------------------------------------

    assert result == []


# ============================================================
# TEST LINUX WSL MOUNT SKIPPING
# ============================================================
# Verifies that /mnt/wslg mount points are skipped on Linux.
# ============================================================

def test_linux_wsl_mount_skipped(monkeypatch):

    partitions = [

        SimpleNamespace(
            device="/dev/sda1",
            mountpoint="/",
            fstype="ext4"
        ),

        SimpleNamespace(
            device="/dev/sdb1",
            mountpoint="/mnt/wslg",
            fstype="ext4"
        )

    ]


    monkeypatch.setattr(
        psutil,
        "disk_partitions",
        lambda: partitions
    )


    monkeypatch.setattr(
        "platform.system",
        lambda: "Linux"
    )


    fake_usage = SimpleNamespace(
        total=100 * (1024 ** 3),
        used=20 * (1024 ** 3),
        free=80 * (1024 ** 3),
        percent=20.0
    )


    monkeypatch.setattr(
        psutil,
        "disk_usage",
        lambda mountpoint: fake_usage
    )


    result = get_disk_usage()


    # --------------------------------------------------------
    # Only the root partition should remain.
    # --------------------------------------------------------

    assert len(result) == 1

    assert result[0]["Mount Point"] == "/"


# ============================================================
# TEST LINUX DOCKER MOUNT SKIPPING
# ============================================================
# Verifies that /var/lib/docker mount points are skipped on
# Linux.
# ============================================================

def test_linux_docker_mount_skipped(monkeypatch):

    partitions = [

        SimpleNamespace(
            device="/dev/sda1",
            mountpoint="/",
            fstype="ext4"
        ),

        SimpleNamespace(
            device="/dev/sdb1",
            mountpoint="/var/lib/docker",
            fstype="ext4"
        )

    ]


    monkeypatch.setattr(
        psutil,
        "disk_partitions",
        lambda: partitions
    )


    monkeypatch.setattr(
        "platform.system",
        lambda: "Linux"
    )


    fake_usage = SimpleNamespace(
        total=100 * (1024 ** 3),
        used=20 * (1024 ** 3),
        free=80 * (1024 ** 3),
        percent=20.0
    )


    monkeypatch.setattr(
        psutil,
        "disk_usage",
        lambda mountpoint: fake_usage
    )


    result = get_disk_usage()


    # --------------------------------------------------------
    # Only the root partition should remain.
    # --------------------------------------------------------

    assert len(result) == 1

    assert result[0]["Mount Point"] == "/"