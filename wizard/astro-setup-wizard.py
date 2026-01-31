import tkinter as tk
from tkinter import messagebox
import subprocess, sys, os

BG_COLOR = "#0f172a"
ACCENT_COLOR = "#38bdf8"

class SetupOrchestrator:
    def __init__(self, root):
        self.root = root
        self.root.title("AstroOrange Setup V6.4")
        self.root.geometry("600x500")
        self.root.configure(bg=BG_COLOR)
        self.wizard_dir = "/opt/astroorange/wizard"
        self.main_content = tk.Frame(self.root, bg=BG_COLOR)
        self.main_content.pack(expand=True, fill="both")
        self.show_welcome()
        self.center_window()

    def show_welcome(self):
        for w in self.main_content.winfo_children(): w.destroy()
        tk.Label(self.main_content, text="🚀", font=("Sans", 60), bg=BG_COLOR).pack(pady=(40, 10))
        tk.Label(self.main_content, text="Bienvenido a AstroOrange", font=("Sans", 24, "bold"), bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=10)
        tk.Label(self.main_content, text="Vamos a configurar tu observatorio.", font=("Sans", 12), bg=BG_COLOR, fg="white").pack(pady=5)
        
        nav = tk.Frame(self.main_content, bg=BG_COLOR)
        nav.pack(side="bottom", pady=40)
        
        self.chk_nomore = tk.BooleanVar(value=False)
        tk.Checkbutton(self.main_content, text="No volver a mostrar este asistente al inicio", variable=self.chk_nomore,
                       bg=BG_COLOR, fg="white", selectcolor=BG_COLOR, font=("Sans", 11), activebackground=BG_COLOR).pack(pady=10)

        tk.Button(nav, text="COMENZAR", command=self.run_user_step, bg=ACCENT_COLOR, fg="black", font=("Sans", 12, "bold"), padx=30, pady=10).pack()

    def run_user_step(self):
        if self.chk_nomore.get():
             subprocess.run("sudo touch /etc/astro-wizard-done", shell=True)
        subprocess.run([sys.executable, f"{self.wizard_dir}/astro-user-gui.py"])
        self.run_net_step()

    def run_net_step(self):
        response = messagebox.askquestion("Paso 2: Red", "¿Deseas configurar una red WiFi ahora?", icon='question')
        if response == 'yes':
            self.run_network_step()
        self.run_soft_step()

    def run_network_step(self):
        splash = tk.Toplevel(self.root)
        splash.geometry("400x150")
        splash.title("Cargando...")
        splash.configure(bg=BG_COLOR)
        w, h = 400, 150
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        splash.geometry(f"+{x}+{y}")
        
        tk.Label(splash, text="⏱️", font=("Sans", 40), bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=(20, 5))
        tk.Label(splash, text="Iniciando Gestor de Red...", font=("Sans", 12, "bold"), bg=BG_COLOR, fg="white").pack(pady=10)
        splash.update()
        
        subprocess.run([sys.executable, f"{self.wizard_dir}/astro-network-gui.py"])
        splash.destroy()

    def run_soft_step(self):
        response = messagebox.askquestion("Paso 3: Software", "¿Deseas abrir el instalador de software astronómico?", icon='question')
        if response == 'yes':
            # V6.4: Check if file exists before running
            soft_path = f"{self.wizard_dir}/astro-software-gui.py"
            if not os.path.exists(soft_path):
                messagebox.showerror("Error", f"No se encuentra: {soft_path}")
            else:
                # Hide main window while software wizard is open
                self.root.withdraw()
                result = subprocess.run([sys.executable, soft_path])
                self.root.deiconify()
                
                if result.returncode != 0:
                    messagebox.showwarning("Aviso", "El instalador de software se cerró inesperadamente.")
        
        # Only show "Finalizado" AFTER software wizard closes
        messagebox.showinfo("✅ Finalizado", "¡Configuración completada!\nDisfruta de AstroOrange.")
        self.root.destroy()
        sys.exit(0)

    def center_window(self):
        self.root.update_idletasks()
        w, h = self.root.winfo_width(), self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"+{x}+{y}")

if __name__ == "__main__":
    # V6.6: Check if user disabled autostart (ONLY when launched from autostart)
    # Manual launches from desktop icons should ALWAYS work
    is_autostart = "--autostart" in sys.argv
    
    if is_autostart and os.path.exists("/etc/astro-wizard-done"):
        sys.exit(0)  # Exit silently if wizard was disabled AND running from autostart
    
    root = tk.Tk()
    app = SetupOrchestrator(root)
    # V6.4: Use system theme icons
    icon_paths = [
        "/usr/share/icons/Papirus/48x48/apps/preferences-system.png",
        "/usr/share/icons/hicolor/48x48/apps/system-installer.png",
        "/usr/share/pixmaps/gdebi.png"
    ]
    for p in icon_paths:
        if os.path.exists(p):
            try: root.iconphoto(False, tk.PhotoImage(file=p)); break
            except: pass
    root.mainloop()
