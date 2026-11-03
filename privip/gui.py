import customtkinter as ctk
import os
import subprocess
import sys
import threading

from . import network
from .config import load_config, save_config

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class PrivIPApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.binary_path = os.path.join(self.base_dir, "bin", "privipchanger")

        self.config = load_config()

        self.title("PrivIP Changer Pro")
        self.geometry("600x700")
        self.setup_ui()
        
        # --- INICIAR MONITOREO ---
        self.check_service_status()
        self.start_auto_refresh() # Inicia el bucle de 5 segundos

    def save_config(self):
        self.config["interface"] = self.interface_var.get()
        save_config(self.config)

    def setup_ui(self):
        # Header
        self.lbl_title = ctk.CTkLabel(self, text="🛡️ IP Protection Dashboard", font=("Roboto", 24, "bold"))
        self.lbl_title.pack(pady=20)

    
        self.frame_iface = ctk.CTkFrame(self)
        self.frame_iface.pack(pady=10, padx=20, fill="x")
        
        self.lbl_iface = ctk.CTkLabel(self.frame_iface, text="Network Interface:")
        self.lbl_iface.pack(side="left", padx=10)
        
        ifaces = network.list_interfaces()
        self.interface_var = ctk.StringVar(value=self.config.get("interface", "wlan0"))
        self.combo = ctk.CTkOptionMenu(self.frame_iface, values=ifaces, variable=self.interface_var, 
                                       command=self.on_interface_change)
        self.combo.pack(side="right", padx=10, pady=10)

 
        self.frame_status = ctk.CTkFrame(self, fg_color="#2b2b2b")
        self.frame_status.pack(pady=15, padx=20, fill="x")

        self.lbl_mac = ctk.CTkLabel(self.frame_status, text="MAC: Scanning...", font=("Consolas", 14), text_color="#2ecc71")
        self.lbl_mac.pack(pady=5)
        
        self.lbl_ip = ctk.CTkLabel(self.frame_status, text="IP: Scanning...", font=("Consolas", 14), text_color="#3498db")
        self.lbl_ip.pack(pady=5)

 
        self.btn_run = ctk.CTkButton(self, text="FORCE IDENTITY CHANGE", fg_color="#c0392b", hover_color="#e74c3c", 
                                     height=45, font=("Roboto", 14, "bold"), command=self.run_manual)
        self.btn_run.pack(pady=10, padx=20, fill="x")

        self.frame_service = ctk.CTkFrame(self)
        self.frame_service.pack(pady=10, padx=20, fill="x")
        
        self.switch_auto = ctk.CTkSwitch(self.frame_service, text="Auto-Change on Firefox Start (Service)", command=self.toggle_service)
        if self.config.get("auto_firefox"): self.switch_auto.select()
        self.switch_auto.pack(pady=15, padx=10)


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
        mac = network.read_mac(iface)
        self.lbl_mac.configure(text=f"MAC: {mac}" if mac else "MAC: Error al leer")

        try:
            ip = network.get_ipv4(iface)
            self.lbl_ip.configure(text=f"IP: {ip or 'Desconectado'}")
        except (OSError, subprocess.SubprocessError):
            self.lbl_ip.configure(text="IP: Error")

    def run_manual(self):
        threading.Thread(target=self._execute_binary).start()

    def _execute_binary(self):
        self.btn_run.configure(state="disabled", text="CHANGING...")
        self.log(f"[EXEC] Running {self.binary_path} on {self.interface_var.get()}...")
        
        try:
            code, stdout, stderr = network.change_identity(self.binary_path, self.interface_var.get())
            if stdout: self.log(f"[STDOUT] {stdout.strip()}")
            if stderr: self.log(f"[STDERR] {stderr.strip()}")
            if code == 0:
                self.log("[DONE] Identity changed.")
            else:
                self.log(f"[FAIL] Binary exited with code {code} - identity NOT changed.")
        except Exception as e:
            self.log(f"[ERROR] {str(e)}")

        self.refresh_network_info()
        self.btn_run.configure(state="normal", text="FORCE IDENTITY CHANGE")

    def toggle_service(self):
        self.config["auto_firefox"] = self.switch_auto.get()
        self.save_config()
        if self.switch_auto.get(): self.install_service()
        else: self.uninstall_service()

    def _service_python(self):
        """El intérprete que debe usar el servicio: el del venv, donde vive psutil."""
        venv_python = os.path.join(self.base_dir, ".venv", "bin", "python")
        if os.path.exists(venv_python):
            return venv_python
        return sys.executable or "/usr/bin/python3"

    def install_service(self):
        network.install_service(self._service_python(), self.base_dir)
        self.log("[SERVICE] Background monitor ENABLED.")

    def uninstall_service(self):
        network.uninstall_service()
        self.log("[SERVICE] Background monitor DISABLED.")

    def check_service_status(self):
        if network.is_service_active():
            self.log("[INFO] El servicio ya está funcionando en segundo plano.")
        else:
            self.log("[INFO] El servicio está detenido.")

    def log(self, msg):
        self.textbox_log.insert("end", msg + "\n")
        self.textbox_log.see("end")

def main():
    PrivIPApp().mainloop()


if __name__ == "__main__":
    main()
