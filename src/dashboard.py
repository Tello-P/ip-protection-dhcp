import customtkinter as ctk
import subprocess
import os
import json
import threading

# Configuración visual
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class PrivIPApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- RUTAS ABSOLUTAS ---
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.binary_path = os.path.join(self.base_dir, "bin", "privipchanger")
        self.monitor_script = os.path.join(self.base_dir, "src", "monitor.py")
        self.config_file = os.path.expanduser("~/.privip_config.json")
        self.service_path = os.path.expanduser("~/.config/systemd/user/privip-monitor.service")

        # Cargar Configuración
        self.config = self.load_config()
        
        # UI Setup
        self.title("PrivIP Changer Pro")
        self.geometry("600x700")
        self.setup_ui()
        
        # --- INICIAR MONITOREO ---
        self.check_service_status()
        self.start_auto_refresh() # Inicia el bucle de 5 segundos

    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {"interface": "wlan0", "auto_firefox": False}

    def save_config(self):
        self.config["interface"] = self.interface_var.get()
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f)

    def setup_ui(self):
        # Header
        self.lbl_title = ctk.CTkLabel(self, text="🛡️ IP Protection Dashboard", font=("Roboto", 24, "bold"))
        self.lbl_title.pack(pady=20)

        # Selector de Interfaz
        self.frame_iface = ctk.CTkFrame(self)
        self.frame_iface.pack(pady=10, padx=20, fill="x")
        
        self.lbl_iface = ctk.CTkLabel(self.frame_iface, text="Network Interface:")
        self.lbl_iface.pack(side="left", padx=10)
        
        ifaces = os.listdir('/sys/class/net/')
        self.interface_var = ctk.StringVar(value=self.config.get("interface", "wlan0"))
        self.combo = ctk.CTkOptionMenu(self.frame_iface, values=ifaces, variable=self.interface_var, 
                                       command=self.on_interface_change)
        self.combo.pack(side="right", padx=10, pady=10)

        # --- PANEL DE ESTADO (IP Y MAC) ---
        self.frame_status = ctk.CTkFrame(self, fg_color="#2b2b2b")
        self.frame_status.pack(pady=15, padx=20, fill="x")

        self.lbl_mac = ctk.CTkLabel(self.frame_status, text="MAC: Scanning...", font=("Consolas", 14), text_color="#2ecc71")
        self.lbl_mac.pack(pady=5)
        
        self.lbl_ip = ctk.CTkLabel(self.frame_status, text="IP: Scanning...", font=("Consolas", 14), text_color="#3498db")
        self.lbl_ip.pack(pady=5)

        # Botón de Cambio Manual
        self.btn_run = ctk.CTkButton(self, text="FORCE IDENTITY CHANGE", fg_color="#c0392b", hover_color="#e74c3c", 
                                     height=45, font=("Roboto", 14, "bold"), command=self.run_manual)
        self.btn_run.pack(pady=10, padx=20, fill="x")

        # Switch de Servicio (Firefox)
        self.frame_service = ctk.CTkFrame(self)
        self.frame_service.pack(pady=10, padx=20, fill="x")
        
        self.switch_auto = ctk.CTkSwitch(self.frame_service, text="Auto-Change on Firefox Start (Service)", command=self.toggle_service)
        if self.config.get("auto_firefox"): self.switch_auto.select()
        self.switch_auto.pack(pady=15, padx=10)

        # Consola de Logs
        self.textbox_log = ctk.CTkTextbox(self, height=180, font=("Consolas", 12))
        self.textbox_log.pack(pady=10, padx=20, fill="both", expand=True)

    # --- LÓGICA DE REFRESCO ---
    def on_interface_change(self, choice):
        self.save_config()
        self.refresh_network_info()
        self.log(f"[INFO] Interfaz cambiada a {choice}")

    def start_auto_refresh(self):
        """Refresca la info de red cada 5 segundos"""
        self.refresh_network_info()
        self.after(5000, self.start_auto_refresh)

    def refresh_network_info(self):
        iface = self.interface_var.get()
        # Obtener MAC
        try:
            with open(f"/sys/class/net/{iface}/address", "r") as f:
                mac = f.read().strip().upper()
                self.lbl_mac.configure(text=f"MAC: {mac}")
        except:
            self.lbl_mac.configure(text="MAC: Error al leer")

        # Obtener IP
        try:
            cmd = f"ip -4 addr show {iface} | grep -oP '(?<=inet\\s)\\d+(\\.\\d+){{3}}' | head -n 1"
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            ip = res.stdout.strip()
            self.lbl_ip.configure(text=f"IP: {ip if ip else 'Desconectado'}")
        except:
            self.lbl_ip.configure(text="IP: Error")

    def run_manual(self):
        threading.Thread(target=self._execute_binary).start()

    def _execute_binary(self):
        self.btn_run.configure(state="disabled", text="CHANGING...")
        self.log(f"[EXEC] Running {self.binary_path} on {self.interface_var.get()}...")
        
        try:
            process = subprocess.Popen([self.binary_path, self.interface_var.get()], 
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate()
            if stdout: self.log(f"[STDOUT] {stdout.strip()}")
            if stderr: self.log(f"[STDERR] {stderr.strip()}")
            self.log("[DONE] Process finished.")
        except Exception as e:
            self.log(f"[ERROR] {str(e)}")
        
        self.refresh_network_info() # Actualizar después de cambiar
        self.btn_run.configure(state="normal", text="FORCE IDENTITY CHANGE")

    def toggle_service(self):
        self.config["auto_firefox"] = self.switch_auto.get()
        self.save_config()
        if self.switch_auto.get(): self.install_service()
        else: self.uninstall_service()

    def install_service(self):
        os.makedirs(os.path.dirname(self.service_path), exist_ok=True)
        content = f"""[Unit]
Description=PrivIP Firefox Watchdog
After=network.target

[Service]
ExecStart=/usr/bin/python3 {self.monitor_script}
Restart=always

[Install]
WantedBy=default.target
"""
        with open(self.service_path, "w") as f: f.write(content)
        subprocess.run(["systemctl", "--user", "daemon-reload"])
        subprocess.run(["systemctl", "--user", "enable", "privip-monitor.service"])
        subprocess.run(["systemctl", "--user", "start", "privip-monitor.service"])
        self.log("[SERVICE] Background monitor ENABLED.")

    def uninstall_service(self):
        subprocess.run(["systemctl", "--user", "stop", "privip-monitor.service"])
        subprocess.run(["systemctl", "--user", "disable", "privip-monitor.service"])
        if os.path.exists(self.service_path): os.remove(self.service_path)
        self.log("[SERVICE] Background monitor DISABLED.")

    def check_service_status(self):
        res = subprocess.run(["systemctl", "--user", "is-active", "privip-monitor.service"], capture_output=True, text=True)
        if res.stdout.strip() == "active":
            self.log("[INFO] El servicio ya está funcionando en segundo plano.")
        else:
            self.log("[INFO] El servicio está detenido.")

    def log(self, msg):
        self.textbox_log.insert("end", msg + "\n")
        self.textbox_log.see("end")

if __name__ == "__main__":
    app = PrivIPApp()
    app.mainloop()
