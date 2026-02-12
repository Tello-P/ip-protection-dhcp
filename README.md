# Interface Manager and DHCP Renew Tool

This project is a C-based utility designed to programmatically manage network interfaces on Linux systems. It specifically focuses on rotating MAC addresses and forcing DHCP lease renewals by simulating DHCP discovery processes.

---

## Overview

The application automates a sequence of network operations typically required for network testing or privacy enhancement. It combines low-level socket programming with the `libpcap` library to interact directly with network hardware and protocol stacks.

### Key Components

* **Interface Manager**: Handles hardware-level operations such as retrieving the current MAC address, incrementing it to a new value, and toggling the interface state (UP/DOWN).
* **DHCP Client**: A custom implementation that crafts and injects DHCP Discovery packets and listens for server offers to obtain a new IP address.
* **Header Definitions**: Organized interfaces via `dhcpClient.h` and `interfaceManager.h` to facilitate modular compilation.

---

## Requirements

To compile and run this project, you need:

* A Linux-based operating system.
* GCC (GNU Compiler Collection).
* `libpcap` development headers.
* Root or sudo privileges (required for `ioctl` calls and raw packet injection).

---

## Installation and Compilation

The project uses a structured directory layout. Ensure your folder structure matches the following:

* `src/`: Source files (`.c`)
* `include/`: Header files (`.h`)
* `bin/`: Compiled executables

To compile the project using the provided Makefile:

```bash
make

```

To remove compiled objects and binaries:

```bash
make clean

```

---

## Usage

Run the executable by providing the name of the network interface you wish to modify:

```bash
sudo ./bin/privipchanger eth0

```

The program will perform the following steps:

1. Set the interface to DOWN state.
2. Calculate and set a new MAC address based on the current one.
3. Set the interface to UP state.
4. Send a DHCP Discovery packet to request a new IP.

---


## Potential Use Cases

* **Privacy and Anonymity**: Periodically changing the MAC address (MAC Spoofing) prevents hardware-based tracking by network administrators or malicious actors in public environments.
* **Mitigating Targeted Network Attacks**: In public Wi-Fi scenarios, constant rotation of both MAC and IP addresses can disrupt active attacks such as ARP Spoofing or targeted session hijacking. By changing network identifiers, an attacker loses the "anchor" they use to intercept or redirect your specific traffic.
* **Bypassing Network Restrictions**: Many captive portals (found in hotels or airports) track data usage or time limits based on the device's MAC address. By automating the change of the MAC and requesting a new IP via DHCP, the system effectively appears as a new device, allowing the user to bypass these enforced limits.
* **Network Testing**: Developers can test how DHCP servers handle rapid lease renewals or hardware address changes.

---

## Learning Objectives

* **Linux Socket Programming**: Using `ioctl` with `SIOCGIFHWADDR` and `SIOCSIFHWADDR` to interact with network interface controllers.
* **Memory Management in C**: Safely handling structures like `ifreq` and performing byte-level manipulations with `memcpy` and `memset`.
* **Network Protocols**: Understanding the DHCP state machine, specifically the structure of Discovery packets and the Boilerplate options required for a valid request.
* **Packet Injection**: Utilizing `libpcap` to bypass the standard TCP/IP stack and inject custom-crafted frames directly into the wire.

---

## License

This project is distributed under the terms specified in the LICENSE file included in the repository.
