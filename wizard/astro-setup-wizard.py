import tkinter as tk
from tkinter import messagebox
import subprocess, sys, os

# --- V6.8: CONFIGURACIÓN SETUP INTEGRAL ---
BG_COLOR = "#0f172a"
ACCENT_COLOR = "#38bdf8"
FG_COLOR = "white"

class SetupOrchestrator:
    def __init__(self, root):
        self.root = root
        self.root.title("AstroOrange Setup V6.8")
        self.root.geometry("600x550") # Un poco más alto para los botones
        self.root.configure(bg=BG_COLOR)
        self.wizard_dir = "/opt/astroorange/wizard"
        self.main_content = tk.Frame(self.root, bg=BG_COLOR)
        self.main_content.pack(expand=True, fill="both")
        self.show_welcome()
        self.center_window()

    def show_welcome(self):
        for w in self.main_content.winfo_children(): w.destroy()
        
        # Header
        tk.Label(self.main_content, text="🚀", font=("Sans", 48), bg=BG_COLOR).pack(pady=(20, 5))
        tk.Label(self.main_content, text="Bienvenido a AstroOrange", font=("Sans", 22, "bold"), bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=5)
        tk.Label(self.main_content, text="Panel de Configuración Integral", font=("Sans", 12), bg=BG_COLOR, fg="white").pack(pady=5)
        
        # --- SECCIÓN PRINCIPAL: MODO GUIADO ---
        frm_guide = tk.Frame(self.main_content, bg=BG_COLOR)
        frm_guide.pack(pady=15, fill="x", padx=40)
        
        tk.Button(frm_guide, text="📚 COMENZAR TUTORIAL GUIADO", command=self.run_tutorial, 
                  bg=ACCENT_COLOR, fg="black", font=("Sans", 12, "bold"), relief="flat", padx=20, pady=12, cursor="hand2").pack(fill="x")
        tk.Label(frm_guide, text="(Usuario → Red Wifi → Software)", font=("Sans", 9), bg=BG_COLOR, fg="#94a3b8").pack(pady=2)

        # Separador visual
        tk.Frame(self.main_content, height=2, bg="#334155").pack(fill="x", padx=40, pady=10)
        
        # --- SECCIÓN HERRAMIENTAS DIRECTAS ---
        tk.Label(self.main_content, text="Acceso Directo a Herramientas:", font=("Sans", 10, "bold"), bg=BG_COLOR, fg="white").pack(pady=(5,10))
        
        frm_tools = tk.Frame(self.main_content, bg=BG_COLOR)
        frm_tools.pack(pady=5)
        
        # Botones individuales
        btn_style = {"bg": "#334155", "fg": "white", "font": ("Sans", 10), "relief": "flat", "width": 25, "pady": 8, "cursor": "hand2"}
        
        tk.Button(frm_tools, text="👤 Configurar Usuario", command=self.open_user_tool, **btn_style).grid(row=0, column=0, padx=5, pady=5)
        tk.Button(frm_tools, text="📡 Configurar Red WiFi", command=self.open_net_tool, **btn_style).grid(row=1, column=0, padx=5, pady=5)
        tk.Button(frm_tools, text="🔭 Instalar Software", command=self.open_soft_tool, **btn_style).grid(row=2, column=0, padx=5, pady=5)

        # Footer con checkbox
        self.chk_nomore = tk.BooleanVar(value=False)
        tk.Checkbutton(self.main_content, text="No volver a mostrar al inicio", variable=self.chk_nomore, command=self.toggle_autostart,
                       bg=BG_COLOR, fg="#cbd5e1", selectcolor=BG_COLOR, font=("Sans", 10), activebackground=BG_COLOR).pack(side="bottom", pady=20)

    # --- ACCIONES ---
    def toggle_autostart(self):
        flag_file = "/etc/astro-wizard-done"
        if self.chk_nomore.get():
             subprocess.run(f"sudo touch {flag_file}", shell=True)
             messagebox.showinfo("Setup", "El asistente ya no se mostrará automáticamente al inicio.")
        else:
             subprocess.run(f"sudo rm -f {flag_file}", shell=True)

    def run_tutorial(self):
        # Flujo paso a paso original
        subprocess.run([sys.executable, f"{self.wizard_dir}/astro-user-gui.py"])
        self.ask_next_step("Paso 2: Red", "¿Deseas configurar una red WiFi ahora?", self.open_net_tool)
        self.ask_next_step("Paso 3: Software", "¿Deseas instalar software astronómico?", self.open_soft_tool)
        messagebox.showinfo("✅ Finalizado", "¡Configuración completada!\nDisfruta de AstroOrange.")
        self.root.destroy()
        sys.exit(0)

    def ask_next_step(self, title, question, func):
        response = messagebox.askquestion(title, question, icon='question')
        if response == 'yes':
            func(wait=True)

    def open_tool(self, script_name, wait=True):
        path = f"{self.wizard_dir}/{script_name}"
        if not os.path.exists(path):
            messagebox.showerror("Error", f"No encontrado: {path}")
            return
        
        self.root.withdraw()
        if wait:
            subprocess.run([sys.executable, path])
        else:
            subprocess.Popen([sys.executable, path])
        self.root.deiconify()

    # Wrappers para cada herramienta
    def open_user_tool(self, wait=True): self.open_tool("astro-user-gui.py", wait)
    def open_net_tool(self, wait=True): self.open_tool("astro-network-gui.py", wait)
    def open_soft_tool(self, wait=True): self.open_tool("astro-software-gui.py", wait)

    def center_window(self):
        self.root.update_idletasks()
        w, h = self.root.winfo_width(), self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"+{x}+{y}")

if __name__ == "__main__":
    # Autocheck para inicio automático
    is_autostart = "--autostart" in sys.argv
    if is_autostart and os.path.exists("/etc/astro-wizard-done"):
        sys.exit(0)
    
    root = tk.Tk()
    app = SetupOrchestrator(root)
    
    # Iconos
    icon_paths = [
        "/usr/share/icons/Papirus/48x48/apps/system-installer.png",
        "/usr/share/pixmaps/gdebi.png"
    ]
    for p in icon_paths:
        if os.path.exists(p):
            try: root.iconphoto(False, tk.PhotoImage(file=p)); break
            except: pass
    root.mainloop()
