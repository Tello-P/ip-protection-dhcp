import time
import psutil
import subprocess
import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BINARY = os.path.join(BASE_DIR, "bin", "privipchanger")
CONFIG_FILE = os.path.expanduser("~/.privip_config.json")

def get_config():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
    except: pass
    return {"interface": "wlan0", "auto_firefox": False}

firefox_was_running = False

while True:
    config = get_config()
    
    if config.get("auto_firefox", False):
        firefox_now = any("firefox" in p.name().lower() for p in psutil.process_iter(['name']))
        
        if firefox_now and not firefox_was_running:
    
            interface = config.get("interface", "wlan0")
            subprocess.run([BINARY, interface])
            
        firefox_was_running = firefox_now
    
    time.sleep(3)
