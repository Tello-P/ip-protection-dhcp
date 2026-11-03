"""Servicio: cambia la identidad cuando se abre Firefox. Ejecutar con `python -m privip.monitor`."""
import os
import subprocess
import time

import psutil

from .config import load_config

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BINARY = os.path.join(BASE_DIR, "bin", "privipchanger")

# Tras salir el binario, el cliente DHCP del sistema aun necesita unos segundos
# para renovar el lease.
SETTLE_SECONDS = 5

FIREFOX_NAMES = {"firefox", "firefox-bin", "firefox-esr"}


def firefox_running():
    for p in psutil.process_iter(['name']):
        name = (p.info.get('name') or "").lower()
        if name in FIREFOX_NAMES:
            return True
    return False


def main():
    firefox_was_running = False
    while True:
        config = load_config()
        if config.get("auto_firefox", False):
            firefox_now = firefox_running()
            if firefox_now and not firefox_was_running:
                subprocess.run([BINARY, config.get("interface", "wlan0")])
                time.sleep(SETTLE_SECONDS)
            firefox_was_running = firefox_now
        time.sleep(3)


if __name__ == "__main__":
    main()
