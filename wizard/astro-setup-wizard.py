import tkinter as tk
from tkinter import messagebox
import subprocess, os, sys

# Estilo Premium AstroOrange
BG_COLOR, SECONDARY_BG, FG_COLOR = "#0f172a", "#1e293b", "#e2e8f0"
ACCENT_COLOR, SUCCESS_COLOR, DANGER_COLOR = "#38bdf8", "#22c55e", "#ef4444"
BUTTON_COLOR = "#334155"

class SetupOrchestrator:
    def __init__(self, root):
        self.root = root
        self.root.title("AstroOrange V2 - Configuración Inicial")
        self.root.geometry("850x600")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)
        
        self.wizard_dir = "/opt/astroorange/wizard"
        if not os.path.exists(self.wizard_dir):
            self.wizard_dir = "." # Fallback para desarrollo local
            
        self.main_content = tk.Frame(self.root, bg=BG_COLOR)
        self.main_content.pack(expand=True, fill="both")
        
        self.show_welcome()

    def clean(self):
        for w in self.main_content.winfo_children(): w.destroy()

    def show_welcome(self):
        self.clean()
        tk.Label(self.main_content, text="🍊 AstroOrange V2", font=("Sans", 36, "bold"), bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=(80, 10))
        tk.Label(self.main_content, text="Bienvenido a tu nueva estación de astrofotografía", font=("Sans", 15), bg=BG_COLOR, fg=FG_COLOR).pack(pady=(0, 50))
        
        info = "Este asistente te ayudará a configurar tu usuario,\nconectar el WiFi e instalar el software necesario."
        tk.Label(self.main_content, text=info, font=("Sans", 13), bg=BG_COLOR, fg=FG_COLOR, justify="center").pack(pady=20)
        
        tk.Button(self.main_content, text="COMENZAR CONFIGURACIÓN", command=self.run_user_step, 
                  bg=ACCENT_COLOR, fg=BG_COLOR, font=("Sans", 14, "bold"), relief="flat", padx=40, pady=15, cursor="hand2").pack(pady=50)

    def run_user_step(self):
        # Lanzar el paso de usuario
        res = subprocess.run([sys.executable, f"{self.wizard_dir}/astro-user-gui.py"])
        # Una vez terminado el de usuario, comprobar si se ha creado (o si existe astro-configured)
        self.run_net_step()

    def run_net_step(self):
        if messagebox.askyesno("Paso 2: Red", "¿Deseas configurar una red WiFi ahora mismo?"):
            subprocess.run([sys.executable, f"{self.wizard_dir}/astro-network-gui.py"])
        
        # Siguiente paso: Software
        self.run_soft_step()

    def run_soft_step(self):
        if messagebox.askyesno("Paso 3: Software", "¿Deseas abrir el instalador de software de astronomía?"):
            subprocess.run([sys.executable, f"{self.wizard_dir}/astro-software-gui.py"])
        
        self.finish()

    def finish(self):
        messagebox.showinfo("Completado", "La configuración inicial ha finalizado.\nPuedes volver a abrir estos asistentes desde el menú del sistema.")
        # Marcar como finalizado para que no autoinicie más
        subprocess.run("sudo touch /etc/astro-wizard-done", shell=True)
        self.root.destroy()

if __name__ == "__main__":
    # Autostart check
    if "--autostart" in sys.argv and os.path.exists("/etc/astro-wizard-done"):
        sys.exit(0)
        
    root = tk.Tk(); app = SetupOrchestrator(root); root.mainloop()
