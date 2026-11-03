"""Llamadas al sistema: ip, systemctl y el binario C (privipchanger).

Todas las funciones aceptan `run` (por defecto subprocess.run) para poder
sustituirlo en los tests sin tocar la red real.
"""
import os
import re
import subprocess

from .mac import normalize_mac

SERVICE_NAME = "privip-monitor.service"
SERVICE_PATH = os.path.expanduser(f"~/.config/systemd/user/{SERVICE_NAME}")
SYS_NET = "/sys/class/net"

_IPV4_RE = re.compile(r"\binet\s+(\d+\.\d+\.\d+\.\d+)")


def list_interfaces(sys_net=SYS_NET):
    return sorted(os.listdir(sys_net))


def read_mac(iface, sys_net=SYS_NET):
    """MAC actual de `iface` en mayúsculas, o None si no se puede leer."""
    try:
        with open(os.path.join(sys_net, iface, "address")) as f:
            return normalize_mac(f.read().strip())
    except (OSError, ValueError):
        return None


def parse_ipv4(ip_output):
    """Extrae la primera IPv4 de la salida de `ip -4 addr show`, o None."""
    m = _IPV4_RE.search(ip_output)
    return m.group(1) if m else None


def get_ipv4(iface, run=subprocess.run):
    """IPv4 de `iface`, None si está desconectada. Lanza OSError/SubprocessError si `ip` falla."""
    res = run(["ip", "-4", "addr", "show", iface], capture_output=True, text=True)
    return parse_ipv4(res.stdout)


def change_identity(binary, iface, run=subprocess.run):
    """Ejecuta el binario C. Devuelve (returncode, stdout, stderr)."""
    res = run([binary, iface], capture_output=True, text=True)
    return res.returncode, res.stdout, res.stderr


def service_unit(python, base_dir):
    """Contenido del unit file de systemd para el monitor."""
    return f"""[Unit]
Description=PrivIP Firefox Watchdog
After=network.target

[Service]
WorkingDirectory={base_dir}
ExecStart={python} -m privip.monitor
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
"""


def _systemctl(*args, run=subprocess.run, **kw):
    return run(["systemctl", "--user", *args], **kw)


def install_service(python, base_dir, path=SERVICE_PATH, run=subprocess.run):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(service_unit(python, base_dir))
    _systemctl("daemon-reload", run=run)
    _systemctl("enable", SERVICE_NAME, run=run)
    _systemctl("start", SERVICE_NAME, run=run)


def uninstall_service(path=SERVICE_PATH, run=subprocess.run):
    _systemctl("stop", SERVICE_NAME, run=run)
    _systemctl("disable", SERVICE_NAME, run=run)
    if os.path.exists(path):
        os.remove(path)


def is_service_active(run=subprocess.run):
    res = _systemctl("is-active", SERVICE_NAME, run=run, capture_output=True, text=True)
    return res.stdout.strip() == "active"
