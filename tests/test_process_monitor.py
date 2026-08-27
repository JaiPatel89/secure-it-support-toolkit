# ============================================================
# PROCESS MONITOR TESTS
# ============================================================
# This module contains automated tests for process_monitor.py.
#
# The tests verify that the process-monitoring module correctly:
#
# - Collects process information
# - Returns process names
# - Returns process IDs
# - Returns process status
# - Calculates CPU usage
# - Calculates memory usage in MB
# - Sorts processes by memory usage
# - Returns only the top 10 processes
# - Handles processes that disappear
# - Handles permission errors
# - Handles zombie processes
# - Handles an empty process list
#
# psutil processes are mocked so that the tests do not depend
# on the actual processes running on the computer.
# ============================================================


# ============================================================
# TEST MODULE PATH
# ============================================================
# The application modules are stored inside the src directory.
#
# The project root is located using pathlib and the src
# directory is added to Python's import path.
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
# psutil:
#     Used to create mocked process behaviour and exceptions.
#
# SimpleNamespace:
#     Creates simple fake process information objects.
#
# process_monitor:
#     Contains the get_processes() function being tested.
# ============================================================

import psutil

from types import SimpleNamespace

from process_monitor import get_processes


# ============================================================
# FAKE PROCESS CLASS
# ============================================================
# This class simulates a psutil.Process object.
#
# It provides the methods and information used by
# process_monitor.py.
# ============================================================


class FakeProcess:

    def __init__(
        self,
        pid,
        name,
        status,
        memory_bytes,
        cpu_percent
    ):

        self.info = {
            "pid": pid,
            "name": name,
            "status": status,
            "memory_info": SimpleNamespace(
                rss=memory_bytes
            )
        }

        self._cpu_percent = cpu_percent


    def cpu_percent(self, interval=None):

        return self._cpu_percent


# ============================================================
# FAKE ERROR PROCESS
# ============================================================
# This class simulates a process that raises a psutil
# exception when its information is accessed.
#
# This more accurately represents the type of error that
# process_monitor.py is designed to handle.
# ============================================================


class FakeErrorProcess:

    def __init__(self, error):

        self.error = error


    @property
    def info(self):

        raise self.error


# ============================================================
# TEST BASIC PROCESS INFORMATION
# ============================================================
# Verifies that process information is collected correctly.
# ============================================================


def test_process_information(monkeypatch):

    fake_process = FakeProcess(
        pid=1234,
        name="TestProcess.exe",
        status="running",
        memory_bytes=104857600,
        cpu_percent=5.5
    )


    monkeypatch.setattr(
        psutil,
        "process_iter",
        lambda information: [fake_process]
    )


    result = get_processes()


    assert len(result) == 1

    assert result[0]["Name"] == "TestProcess.exe"

    assert result[0]["PID"] == 1234

    assert result[0]["Status"] == "running"

    assert result[0]["CPU Usage"] == "5.5%"

    assert result[0]["Memory Usage (MB)"] == 100.0


# ============================================================
# TEST MEMORY CONVERSION
# ============================================================
# Verifies that RSS memory in bytes is correctly converted
# into megabytes.
# ============================================================


def test_memory_conversion(monkeypatch):

    fake_process = FakeProcess(
        pid=100,
        name="MemoryTest.exe",
        status="running",
        memory_bytes=52428800,
        cpu_percent=2.0
    )


    monkeypatch.setattr(
        psutil,
        "process_iter",
        lambda information: [fake_process]
    )


    result = get_processes()


    assert (
        result[0]["Memory Usage (MB)"]
        == 50.0
    )


# ============================================================
# TEST CPU USAGE
# ============================================================
# Verifies that CPU usage is returned with a percentage sign.
# ============================================================


def test_cpu_usage(monkeypatch):

    fake_process = FakeProcess(
        pid=200,
        name="CPUProcess.exe",
        status="running",
        memory_bytes=1048576,
        cpu_percent=25.7
    )


    monkeypatch.setattr(
        psutil,
        "process_iter",
        lambda information: [fake_process]
    )


    result = get_processes()


    assert result[0]["CPU Usage"] == "25.7%"


# ============================================================
# TEST SORTING
# ============================================================
# Verifies that processes are sorted from highest memory usage
# to lowest memory usage.
# ============================================================


def test_processes_sorted_by_memory(monkeypatch):

    processes = [

        FakeProcess(
            pid=1,
            name="LowMemory.exe",
            status="running",
            memory_bytes=10485760,
            cpu_percent=1.0
        ),

        FakeProcess(
            pid=2,
            name="HighMemory.exe",
            status="running",
            memory_bytes=524288000,
            cpu_percent=5.0
        ),

        FakeProcess(
            pid=3,
            name="MediumMemory.exe",
            status="running",
            memory_bytes=104857600,
            cpu_percent=3.0
        )

    ]


    monkeypatch.setattr(
        psutil,
        "process_iter",
        lambda information: processes
    )


    result = get_processes()


    assert result[0]["Name"] == "HighMemory.exe"

    assert result[1]["Name"] == "MediumMemory.exe"

    assert result[2]["Name"] == "LowMemory.exe"


# ============================================================
# TEST TOP 10 PROCESSES
# ============================================================
# Verifies that only the ten processes using the most memory
# are returned when more than ten processes are available.
# ============================================================


def test_returns_top_10_processes(monkeypatch):

    processes = []


    for number in range(15):

        processes.append(
            FakeProcess(
                pid=number,
                name=f"Process{number}.exe",
                status="running",
                memory_bytes=(number + 1) * 1048576,
                cpu_percent=1.0
            )
        )


    monkeypatch.setattr(
        psutil,
        "process_iter",
        lambda information: processes
    )


    result = get_processes()


    assert len(result) == 10

    assert result[0]["Name"] == "Process14.exe"

    assert result[-1]["Name"] == "Process5.exe"


# ============================================================
# TEST NO SUCH PROCESS
# ============================================================
# Simulates a process disappearing while its information is
# being accessed.
#
# process_monitor.py should catch NoSuchProcess and continue
# processing the remaining processes.
# ============================================================


def test_handles_no_such_process(monkeypatch):

    valid_process = FakeProcess(
        pid=123,
        name="ValidProcess.exe",
        status="running",
        memory_bytes=10485760,
        cpu_percent=1.0
    )


    invalid_process = FakeErrorProcess(
        psutil.NoSuchProcess(pid=999)
    )


    monkeypatch.setattr(
        psutil,
        "process_iter",
        lambda information: [
            invalid_process,
            valid_process
        ]
    )


    result = get_processes()


    assert len(result) == 1

    assert (
        result[0]["Name"]
        == "ValidProcess.exe"
    )


# ============================================================
# TEST ACCESS DENIED
# ============================================================
# Simulates a process that cannot be accessed because the
# current user does not have sufficient permissions.
#
# process_monitor.py should ignore the process and continue.
# ============================================================


def test_handles_access_denied(monkeypatch):

    valid_process = FakeProcess(
        pid=456,
        name="AccessibleProcess.exe",
        status="running",
        memory_bytes=20971520,
        cpu_percent=2.0
    )


    denied_process = FakeErrorProcess(
        psutil.AccessDenied(pid=999)
    )


    monkeypatch.setattr(
        psutil,
        "process_iter",
        lambda information: [
            denied_process,
            valid_process
        ]
    )


    result = get_processes()


    assert len(result) == 1

    assert (
        result[0]["Name"]
        == "AccessibleProcess.exe"
    )


# ============================================================
# TEST ZOMBIE PROCESS
# ============================================================
# Simulates a zombie process.
#
# process_monitor.py should ignore the zombie process rather
# than allowing the exception to stop the application.
# ============================================================


def test_handles_zombie_process(monkeypatch):

    valid_process = FakeProcess(
        pid=789,
        name="NormalProcess.exe",
        status="running",
        memory_bytes=31457280,
        cpu_percent=3.0
    )


    zombie_process = FakeErrorProcess(
        psutil.ZombieProcess(pid=999)
    )


    monkeypatch.setattr(
        psutil,
        "process_iter",
        lambda information: [
            zombie_process,
            valid_process
        ]
    )


    result = get_processes()


    assert len(result) == 1

    assert (
        result[0]["Name"]
        == "NormalProcess.exe"
    )


# ============================================================
# TEST EMPTY PROCESS LIST
# ============================================================
# Verifies that the function safely handles a situation where
# no processes are returned.
# ============================================================


def test_empty_process_list(monkeypatch):

    monkeypatch.setattr(
        psutil,
        "process_iter",
        lambda information: []
    )


    result = get_processes()


    assert result == []


# ============================================================
# TEST PROCESS STATUS
# ============================================================
# Verifies that the process status is returned unchanged.
# ============================================================


def test_process_status(monkeypatch):

    fake_process = FakeProcess(
        pid=999,
        name="SleepingProcess.exe",
        status="sleeping",
        memory_bytes=4194304,
        cpu_percent=0.0
    )


    monkeypatch.setattr(
        psutil,
        "process_iter",
        lambda information: [fake_process]
    )


    result = get_processes()


    assert (
        result[0]["Status"]
        == "sleeping"
    )

