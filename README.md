# PrivIP Protection & DHCP Changer

A Linux utility for network identity rotation.

This project combines a C-based engine for low-level packet injection with a Python GUI and a Systemd background service to automate privacy.

## Key Features

- **Core Engine (C)**: Programmatic MAC address rotation and raw DHCP packet injection using libpcap and ioctl.
- **Modern GUI (Python)**: Intuitive dashboard built with CustomTkinter for real-time monitoring and control.
- **Firefox Watchdog**: An automated service that triggers an identity change the moment you open your browser.
- **Systemd Integration**: Runs as a background daemon, ensuring protection even if the GUI is closed.
- **Identity Refresh**: Forces DHCP lease renewals to obtain a new IP address, effectively appearing as a new device to the network.

## Requirements

- **OS**: Linux (Arch recommended).
- **Compiler**: GCC.
- **Libraries**: libpcap-dev, python3-venv, python3-tk.
- **Permissions**: The installer automatically configures setcap so you can run the tool without sudo for daily use.

## Installation

The provided install script automates the entire process: system dependencies, C compilation, and Python virtual environment setup.

```bash
git clone https://github.com/your-user/ip-protection-dhcp.git
cd ip-protection-dhcp
chmod +x scripts/install.sh
./scripts/install.sh
```

## Usage

### 1. Graphical User Interface (GUI)

The GUI is the recommended way to use the tool. It provides real-time MAC/IP monitoring.

```bash
source .venv/bin/activate
python src/dashboard.py
```

**GUI Features:**
- Interface Selector: Choose between wlan0, eth0, etc.
- Force Identity Change: Manual trigger to rotate MAC and IP immediately.
- Auto-Change (Firefox): Toggle the background service that watches for browser activity.
- Live Console: View the raw output from the C engine.

### 2. Background Service (CLI/Service)

Once the "Auto-Change" is enabled in the GUI, a Systemd user service is created. It operates silently in the background.

- Check Status:
  ```bash
  systemctl --user status privip-monitor.service
  ```

- View Logs:
  ```bash
  journalctl --user -u privip-monitor.service -f
  ```

### 3. Manual CLI Mode

If you prefer the command line, you can run the compiled binary directly:

```bash
# Usage: ./bin/privipchanger <interface>
sudo ./bin/privipchanger wlan0
```

## Technical Architecture

- **Interface Manager**: Set interface DOWN, calculates a new hardware address, and brings it UP.
- **DHCP Client**: Crafts a custom DHCP packet, bypassing the standard OS stack via libpcap to request a fresh lease.
- **Python Bridge**: Uses subprocess and threading to communicate with the C binary.
- **Persistence**: User preferences are stored in `~/.privip_config.json`.

## Use Cases

- Privacy & Anonymity: Prevent hardware-based tracking in public environments.
- Bypass Restrictions: Circumvent time or data limits on captive portals (hotels/airports) by appearing as a new device.
- Security Testing: Test how DHCP servers handle rapid lease renewals and hardware address changes.

## Learning Objectives

This project explores several advanced concepts:

- Linux Socket Programming: Using SIOCGIFHWADDR and SIOCSIFHWADDR.
- Packet Injection: Using libpcap for manual frame construction.
- Daemonization: Managing background processes via systemd.
- Hybrid Development: Bridging low-level C logic with high-level Python GUIs.

## License & Disclaimer

See [LICENSE](LICENSE) for more information.

**Disclaimer**: This tool is for educational and personal security purposes. Use it responsibly and only on networks you own or have permission to test.
