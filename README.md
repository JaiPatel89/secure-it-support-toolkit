Secure IT Support Toolkit

A cross-platform Python toolkit designed to assist IT support technicians and system administrators with common diagnostic and troubleshooting tasks.

This project was developed to strengthen my Python programming skills while building a practical tool that reflects real-world IT support workflows. It provides system information, network diagnostics, firewall checks, disk usage monitoring and process monitoring through a simple command-line interface.


Features:

System Information
    -Display operating system information
    -View hostname
    -Display CPU information
    -View installed memory (RAM)

Network Information
    -Display network interfaces
    -View IPv4 addresses
    -Display MAC addresses

Firewall Status
    -Check firewall status on Windows
    -Check firewall status on Linux
    -macOS support implemented

Disk Usage
    -Display all available drives
    -Show total, used and free storage
    -Display disk usage percentage
    -Cross-platform support

Process Monitor
    -Display running processes
    -Show memory usage
    -Show CPU utilisation
    -Sort processes by memory usage

Network Diagnostics
    -Internet connectivity test
    -DNS resolution test
    -Local IP address
    -Default gateway detection
    -Ping latency
    -Packet loss

Technologies Used
    -Python 3
    -psutil
    -subprocess
    -socket
    -platform

Supported Platforms
    Platform	        Status
    Windows	            ✅ Tested
    Linux (Kali WSL)    ✅ Tested
    macOS	            ⚠️ Support implemented but not yet tested


Installation

Clone the repository:

git clone https://github.com/JaiPatel89/Secure-IT-Support-Toolkit.git

Navigate into the project:

cd Secure-IT-Support-Toolkit/src

Install the required dependency:

pip install -r requirements.txt

Run the application:

python main.py


Project Structure
Secure-IT-Support-Toolkit
│
├── src
│   ├── main.py
│   ├── system_info.py
│   ├── network_tools.py
│   ├── firewall_status.py
│   ├── disk_usage.py
│   ├── process_monitor.py
│   └── network_diagnostics.py
│
├── requirements.txt
├── README.md
└── LICENSE


Future Improvements
    -Export diagnostic reports
    -Logging functionality
    -Live system monitoring
    -Additional network diagnostics
    -Graphical user interface (GUI)
    -Automated health checks


Why I Built This Project

I wanted to create a practical project that demonstrates Python programming, troubleshooting and system administration skills while producing a tool that could genuinely assist an IT support technician.

The project focuses on writing clean, modular code and implementing cross-platform functionality wherever possible.

Author

Jai Patel

GitHub: https://github.com/JaiPatel89