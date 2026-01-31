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
        tk.Label(self.main_content, text="🍊 AstroOrange V2", font=("Sans", 36, "bold"), bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=(60, 10))
        tk.Label(self.main_content, text="Bienvenido a tu nueva estación de astrofotografía", font=("Sans", 15), bg=BG_COLOR, fg=FG_COLOR).pack(pady=(0, 40))
        
        info = "Este asistente te ayudará a configurar tu usuario,\nconectar el WiFi e instalar el software necesario."
        tk.Label(self.main_content, text=info, font=("Sans", 13), bg=BG_COLOR, fg=FG_COLOR, justify="center").pack(pady=20)
        
        # Don't show again checkbox
        self.chk_nomore = tk.BooleanVar(value=False)
        tk.Checkbutton(self.main_content, text="No volver a mostrar este asistente al inicio", variable=self.chk_nomore,
                       bg=BG_COLOR, fg="white", selectcolor=BG_COLOR, font=("Sans", 11), activebackground=BG_COLOR).pack(pady=10)

        tk.Button(self.main_content, text="COMENZAR CONFIGURACIÓN", command=self.run_user_step, 
                  bg=ACCENT_COLOR, fg=BG_COLOR, font=("Sans", 14, "bold"), relief="flat", padx=40, pady=15, cursor="hand2").pack(pady=40)

    def run_user_step(self):
        # Handle "Don't show again" logic immediately if checked
        if self.chk_nomore.get():
             subprocess.run("sudo touch /etc/astro-wizard-done", shell=True)

        # Lanzar el paso de usuario
        res = subprocess.run([sys.executable, f"{self.wizard_dir}/astro-user-gui.py"])
        self.run_net_step()

    def run_net_step(self):
        if messagebox.askyesno("Paso 2: Red", "¿Deseas configurar una red WiFi ahora mismo?"):
            subprocess.run([sys.executable, f"{self.wizard_dir}/astro-network-gui.py"])
        
        self.run_soft_step()

    def run_soft_step(self):
        # Force software installer if potential updates/installs needed, or just ask
        if messagebox.askyesno("Paso 3: Software", "¿Deseas abrir el instalador de software de astronomía?"):
             subprocess.run([sys.executable, f"{self.wizard_dir}/astro-software-gui.py"])
        
        self.finish()

    def finish(self):
        messagebox.showinfo("Completado", "La configuración inicial ha finalizado.\nPuedes volver a abrir estos asistentes desde el menú del sistema.")
        self.root.destroy()

    def center_window(self):
        self.root.update_idletasks()
        w, h = self.root.winfo_width(), self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"+{x}+{y}")

if __name__ == "__main__":
    # Autostart check
    if "--autostart" in sys.argv and os.path.exists("/etc/astro-wizard-done"):
        sys.exit(0)
        
    root = tk.Tk()
    app = SetupOrchestrator(root)
    app.center_window()
    
    # Robust Icon Loading
    icon_paths = [
        "/usr/share/icons/Papirus/32x32/apps/system-installer.png",
        "/usr/share/icons/hicolor/48x48/apps/system-installer.png",
        "/usr/share/icons/Adwaita/48x48/emblems/emblem-system.png"
    ]
    for p in icon_paths:
        if os.path.exists(p):
            try:
                img = tk.PhotoImage(file=p)
                root.iconphoto(False, img)
                break
            except: pass
            
    root.mainloop()
