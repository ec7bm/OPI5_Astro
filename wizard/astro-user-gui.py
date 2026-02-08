import subprocess, time, os
import tkinter as tk
from tkinter import messagebox, ttk
import i18n


# Estilo Premium AstroOrange
BG_COLOR, SECONDARY_BG, FG_COLOR = "#0f172a", "#1e293b", "#e2e8f0"
ACCENT_COLOR, SUCCESS_COLOR, DANGER_COLOR = "#38bdf8", "#22c55e", "#ef4444"
BUTTON_COLOR = "#334155"

class UserWizard:
    def __init__(self, root):
        self.root = root
        self.root.title(i18n.t("user_manager"))

        self.root.geometry("800x600")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)
        
        self.main_content = tk.Frame(self.root, bg=BG_COLOR)
        self.main_content.pack(expand=True, fill="both")
        
        self.center_window()
        self.draw_main()

    def center_window(self):
        self.root.update_idletasks()
        w, h = self.root.winfo_width(), self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"+{x}+{y}")

    def clean(self):

        for w in self.main_content.winfo_children(): w.destroy()

    def head(self, t, s=""):
        tk.Label(self.main_content, text="👤 " + t, font=("Sans", 32, "bold"), bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=(50, 5))
        if s: tk.Label(self.main_content, text=s, font=("Sans", 14), bg=BG_COLOR, fg=FG_COLOR).pack(pady=(0, 40))

    def btn(self, parent, text, cmd, color=BUTTON_COLOR, width=18):
        return tk.Button(parent, text=text, command=cmd, bg=color, fg="white", 
                         font=("Sans", 11, "bold"), relief="flat", padx=25, pady=12, 
                         activebackground=ACCENT_COLOR, cursor="hand2", width=width)

    def draw_main(self):
        self.clean()
        
        # --- CONTAINER CENTRADO (SOLUCIÓN V10.8) ---
        # Usamos place() para centrar matemáticamente un frame contenedor
        # Esto asegura que NUNCA se pierdan los botones por resolución
        container = tk.Frame(self.main_content, bg=BG_COLOR)
        container.place(relx=0.5, rely=0.5, anchor="center")
        
        # 1. Cabecera (Dentro del container)
        tk.Label(container, text="👤 " + i18n.t("create_user"), font=("Sans", 32, "bold"), bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=(0, 10))
        tk.Label(container, text="Configura los datos del nuevo operador", font=("Sans", 14), bg=BG_COLOR, fg=FG_COLOR).pack(pady=(0, 30))
        
        # 2. Formulario (Dentro del container)
        f = tk.Frame(container, bg=SECONDARY_BG, padx=40, pady=40)
        f.pack(pady=10)
        
        tk.Label(f, text=i18n.t("username").upper(), bg=SECONDARY_BG, fg=ACCENT_COLOR, font=("Sans", 10, "bold")).pack(anchor="w")
        self.eu = tk.Entry(f, width=30, font=("Sans", 14), bg=BG_COLOR, fg="white", bd=0, insertbackground="white", highlightthickness=1, highlightbackground=BUTTON_COLOR)
        self.eu.pack(pady=(5, 20), ipady=8)
        
        tk.Label(f, text=i18n.t("password").upper(), bg=SECONDARY_BG, fg=ACCENT_COLOR, font=("Sans", 10, "bold")).pack(anchor="w")
        self.ep = tk.Entry(f, show="*", width=30, font=("Sans", 14), bg=BG_COLOR, fg="white", bd=0, insertbackground="white", highlightthickness=1, highlightbackground=BUTTON_COLOR)
        self.ep.pack(pady=(5, 5), ipady=8)
        
        # Show Password Toggle
        self.show_pass = tk.BooleanVar(value=False)
        tk.Checkbutton(f, text="Mostrar contraseña", variable=self.show_pass, command=self.toggle_password,
                       bg=SECONDARY_BG, fg="white", selectcolor=BG_COLOR, font=("Sans", 9)).pack(anchor="w", pady=0)

        # Auto-login
        self.chk_autologin = tk.BooleanVar(value=True)
        tk.Checkbutton(f, text=i18n.t("autologin"), variable=self.chk_autologin,
                       bg=SECONDARY_BG, fg="white", selectcolor=BG_COLOR, font=("Sans", 10)).pack(anchor="w", pady=15)
        
        # 3. Botones (Dentro del container, SIEMPRE VISIBLES)
        nav = tk.Frame(container, bg=BG_COLOR)
        nav.pack(pady=30)
        
        self.btn(nav, "CANCELAR", self.root.destroy, DANGER_COLOR, width=15).pack(side="left", padx=15)
        self.btn(nav, i18n.t("save").upper(), self.create, ACCENT_COLOR, width=15).pack(side="left", padx=15)


    def toggle_password(self):
        self.ep.config(show="" if self.show_pass.get() else "*")

    def create(self):
        u, p = self.eu.get().strip(), self.ep.get().strip()
        if len(u) < 3 or len(p) < 4: messagebox.showwarning("Error", "Mínimo 3 chars nombre y 4 pass"); return
        try: subprocess.check_call(["id", "-u", u], stdout=subprocess.DEVNULL); messagebox.showerror("Error", f"Usuario {u} existe"); return
        except: pass
        
        # Create User
        # V13.1: Hardened creation with explicit error checking
        try:
            self.log("   --- CREATING SYSTEM USER ---")
            subprocess.check_call(f"sudo useradd -m -s /bin/bash {u}", shell=True)
            subprocess.check_call(f"echo '{u}:{p}' | sudo chpasswd", shell=True)
            
            # V11.4.1: Add groups individually to avoid failure if one is missing
            target_groups = ["sudo", "dialout", "video", "render", "input", "plugdev", "audio", "vnc", "novnc"]
            for g in target_groups:
                subprocess.run(f"sudo groupadd {g} 2>/dev/null", shell=True)
                subprocess.run(f"sudo usermod -aG {g} {u} 2>/dev/null", shell=True)

            # V11.4: Provision Desktop Icons for the new user
            desktop_dir = f"/home/{u}/Desktop"
            subprocess.run(f"sudo mkdir -p {desktop_dir}", shell=True)
            app_src = "/usr/share/applications"
            for app in ["astro-network.desktop", "astro-software.desktop", "astro-user.desktop"]:
                if os.path.exists(f"{app_src}/{app}"):
                    subprocess.run(f"sudo cp {app_src}/{app} {desktop_dir}/", shell=True)
            
            subprocess.run(f"sudo chmod +x {desktop_dir}/*.desktop", shell=True)
            subprocess.run(f"sudo chown -R {u}:{u} /home/{u}", shell=True)
            
            if self.chk_autologin.get():
                cfg = f"[Seat:*]\nautologin-user={u}\nautologin-session=xfce\nautologin-user-timeout=0\n"
                with open("/tmp/60-astro-user.conf", "w") as f: f.write(cfg)
                subprocess.run("sudo rm -f /etc/lightdm/lightdm.conf.d/50-setup.conf", shell=True)
                subprocess.run("sudo mv /tmp/60-astro-user.conf /etc/lightdm/lightdm.conf.d/60-astro-user.conf", shell=True)
                subprocess.run(["sync"])
            
            # V13.1 Nuclear Sync
            self.log("   --- FLUSHING TO DISK ---")
            for _ in range(3):
                subprocess.run(["sync"])
                time.sleep(1)
            
            messagebox.showinfo("Éxito", f"Usuario '{u}' creado correctamente.")
            self.root.destroy()
            
        except Exception as e:
            err_msg = f"ERROR CRÍTICO AL CREAR USUARIO:\n{str(e)}"
            self.log(err_msg)
            messagebox.showerror("Error de Sistema", err_msg)

    def log(self, msg):
        print(f"[USER-WIZARD] {msg}")

if __name__ == "__main__":
    import tkinter as tk
    from tkinter import messagebox
    root = tk.Tk(); app = UserWizard(root); root.mainloop()

