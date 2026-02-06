import subprocess, sys, os
import i18n


# --- V6.9: SETUP UI PROFESIONAL (SIN EMOJIS ROTOS) ---
BG_COLOR = "#0f172a"
ACCENT_COLOR = "#38bdf8"
BTN_BG = "#1e293b"      # Color de fondo de botones secundarios
BTN_FG = "#e2e8f0"      # Color de texto de botones secundarios

class SetupOrchestrator:
    def __init__(self, root):
        self.root = root
        
        # V13.0: Verificación inicial de idioma
        if not os.path.exists(i18n.LANG_FILE):
             self.open_tool("astro-language-selector.py", wait=True)
             
        self.root.title(f"AstroOrange Setup V7.5 ({i18n.get_lang().upper()})")

        self.root.geometry("600x650") 
        self.root.configure(bg=BG_COLOR)
        self.wizard_dir = "/opt/astroorange/wizard"
        self.icons = {} 
        
        self.main_content = tk.Frame(self.root, bg=BG_COLOR)
        self.main_content.pack(expand=True, fill="both", padx=20, pady=20)
        
        self.show_welcome()
        self.center_window()

    def load_icon(self, names, size=32):
        """Carga el primer icono encontrado de una lista de nombres"""
        if isinstance(names, str): names = [names]
        
        for name in names:
            paths = [
                f"/usr/share/icons/Papirus/{size}x{size}/apps/{name}.png",
                f"/usr/share/icons/Papirus/{size}x{size}/categories/{name}.png",
                f"/usr/share/icons/Papirus/{size}x{size}/devices/{name}.png",
                f"/usr/share/icons/hicolor/{size}x{size}/apps/{name}.png",
                f"/usr/share/pixmaps/{name}.png"
            ]
            for p in paths:
                if os.path.exists(p):
                    try: return tk.PhotoImage(file=p)
                    except: pass
        return None

    def show_welcome(self):
        for w in self.main_content.winfo_children(): w.destroy()
        
        # --- HEADER ---
        # Icono Telescope o Science
        logo = self.load_icon(["telescope", "applications-science", "kstars"], 64)
        if logo:
            lbl_logo = tk.Label(self.main_content, image=logo, bg=BG_COLOR)
            lbl_logo.image = logo
            lbl_logo.pack(pady=(10, 5))
        else:
            tk.Label(self.main_content, text="🔭", font=("Sans", 48), bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=(10,5))
        
        tk.Label(self.main_content, text="AstroOrange", font=("Sans", 28, "bold"), bg=BG_COLOR, fg=ACCENT_COLOR).pack()
        tk.Label(self.main_content, text="Panel de Configuración", font=("Sans", 14), bg=BG_COLOR, fg="#94a3b8").pack(pady=(0, 20))
        
        # --- SECCIÓN GUIADA ---
        frm_guide = tk.Frame(self.main_content, bg=BG_COLOR, bd=1, relief="solid")
        frm_guide.pack(fill="x", pady=10)
        
        tk.Label(frm_guide, text="Recomendado para empezar:", font=("Sans", 10), bg=BG_COLOR, fg="white").pack(anchor="w", padx=10, pady=5)
        
        btn_guide = tk.Button(frm_guide, text="INICIAR TUTORIAL COMPLETO", command=self.run_tutorial, 
                              bg=ACCENT_COLOR, fg="#0f172a", font=("Sans", 12, "bold"), relief="flat", padx=20, pady=15, cursor="hand2")
        btn_guide.pack(fill="x", padx=10, pady=(0, 10))

        # --- SECCIÓN HERRAMIENTAS ---
        tk.Label(self.main_content, text="Herramientas Individuales:", font=("Sans", 10, "bold"), bg=BG_COLOR, fg="white").pack(anchor="w", pady=(20, 5))
        
        # Cargar iconos específicos
        self.icons['user'] = self.load_icon(["avatar-default", "system-users", "preferences-desktop-user"], 24)
        self.icons['wifi'] = self.load_icon(["network-wireless", "preferences-system-network"], 24)
        self.icons['soft'] = self.load_icon(["system-software-install", "applications-science", "synaptic"], 24)
        
        # Grid de botones
        frm_tools = tk.Frame(self.main_content, bg=BG_COLOR)
        frm_tools.pack(fill="x")
        
        self.create_tool_btn(frm_tools, i18n.t("config_user"), self.icons.get('user'), self.open_user_tool)
        self.create_tool_btn(frm_tools, i18n.t("config_wifi"), self.icons.get('wifi'), self.open_net_tool)
        self.create_tool_btn(frm_tools, i18n.t("install_soft"), self.icons.get('soft'), self.open_soft_tool)
        self.create_tool_btn(frm_tools, i18n.t("select_language"), None, self.open_lang_tool)


        # --- FOOTER CHECKBOX ---
        # Frame separador para empujar el checkbox abajo
        tk.Frame(self.main_content, bg=BG_COLOR).pack(expand=True)
        
        self.chk_nomore = tk.BooleanVar(value=False)
        chk = tk.Checkbutton(self.main_content, text=i18n.t("no_more_show"), variable=self.chk_nomore, command=self.toggle_autostart,
                       bg=BG_COLOR, fg="#cbd5e1", selectcolor=BG_COLOR, font=("Sans", 10), activebackground=BG_COLOR, cursor="hand2")
        chk.pack(side="bottom", pady=20)


    def create_tool_btn(self, parent, text, icon, command):
        """Crea un botón estilizado con icono opcional"""
        btn = tk.Button(parent, text=f"  {text}", command=command, compound="left",
                        bg=BTN_BG, fg=BTN_FG, font=("Sans", 11), relief="flat", 
                        width=30, padx=20, pady=10, anchor="w", cursor="hand2")
        if icon:
            btn.config(image=icon)
            btn.image = icon # Mantener referencia
        
        btn.pack(fill="x", pady=4)
        
        # Efecto hover simple
        btn.bind("<Enter>", lambda e: btn.config(bg="#334155"))
        btn.bind("<Leave>", lambda e: btn.config(bg=BTN_BG))

    # --- ACCIONES ---
    def toggle_autostart(self):
        flag_file = "/etc/astro-wizard-done"
        if self.chk_nomore.get():
             subprocess.run(f"sudo touch {flag_file}", shell=True)
             messagebox.showinfo("Setup", i18n.t("setup_done_msg"))
        else:
             subprocess.run(f"sudo rm -f {flag_file}", shell=True)


    def run_tutorial(self):
        self.open_user_tool(wait=True)
        self.ask_next_step("Setup", i18n.t("ask_wifi"), self.open_net_tool)
        self.ask_next_step("Setup", i18n.t("ask_software"), self.open_soft_tool)
        messagebox.showinfo("AstroOrange", i18n.t("tutorial_complete"))
        self.root.destroy()
        sys.exit(0)


    def ask_next_step(self, title, question, func):
        if messagebox.askyesno(title, question):
            func(wait=True)

    def open_tool(self, script_name, wait=True):
        path = f"{self.wizard_dir}/{script_name}"
        if not os.path.exists(path):
            messagebox.showerror("Error", f"No encontrado: {path}")
            return
        
        self.root.withdraw()
        try:
            if wait:
                subprocess.run([sys.executable, path], check=True)
            else:
                subprocess.Popen([sys.executable, path])
        except Exception as e:
            messagebox.showerror("Error", f"Fallo al ejecutar {script_name}:\n{e}")
        
        self.root.deiconify()


    def open_user_tool(self, wait=True): self.open_tool("astro-user-gui.py", wait); self.show_welcome()
    def open_net_tool(self, wait=True): self.open_tool("astro-network-gui.py", wait); self.show_welcome()
    def open_soft_tool(self, wait=True): self.open_tool("astro-software-gui.py", wait); self.show_welcome()
    def open_lang_tool(self, wait=True): self.open_tool("astro-language-selector.py", wait); self.show_welcome()


    def center_window(self):
        self.root.update_idletasks()
        w, h = self.root.winfo_width(), self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"+{x}+{y}")

if __name__ == "__main__":
    is_autostart = "--autostart" in sys.argv
    if is_autostart and os.path.exists("/etc/astro-wizard-done"):
        sys.exit(0)
    
    root = tk.Tk()
    app = SetupOrchestrator(root)
    
    # Icono ventana
    try:
        icon_path = "/usr/share/icons/Papirus/48x48/apps/system-installer.png"
        if os.path.exists(icon_path):
            root.iconphoto(False, tk.PhotoImage(file=icon_path))
    except: pass
    
    root.mainloop()
