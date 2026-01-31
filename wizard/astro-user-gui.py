import tkinter as tk
from tkinter import messagebox
import subprocess

# Estilo Premium AstroOrange
BG_COLOR, SECONDARY_BG, FG_COLOR = "#0f172a", "#1e293b", "#e2e8f0"
ACCENT_COLOR, SUCCESS_COLOR, DANGER_COLOR = "#38bdf8", "#22c55e", "#ef4444"
BUTTON_COLOR = "#334155"

class UserWizard:
    def __init__(self, root):
        self.root = root
        self.root.title("AstroOrange User Manager")
        self.root.geometry("700x600")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)
        
        self.main_content = tk.Frame(self.root, bg=BG_COLOR)
        self.main_content.pack(expand=True, fill="both")
        
        self.draw_main()

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
        self.clean(); self.head("Nuevo Usuario", "Configura los datos del nuevo operador")
        
        f = tk.Frame(self.main_content, bg=SECONDARY_BG, padx=50, pady=50, bd=0); f.pack(pady=10)
        
        tk.Label(f, text="NOMBRE DE USUARIO", bg=SECONDARY_BG, fg=ACCENT_COLOR, font=("Sans", 10, "bold")).pack(anchor="w")
        self.eu = tk.Entry(f, width=35, font=("Sans", 14), bg=BG_COLOR, fg="white", bd=0, insertbackground="white", highlightthickness=1, highlightbackground=BUTTON_COLOR)
        self.eu.pack(pady=(10, 30), ipady=10)
        
        tk.Label(f, text="CONTRASEÑA", bg=SECONDARY_BG, fg=ACCENT_COLOR, font=("Sans", 10, "bold")).pack(anchor="w")
        self.ep = tk.Entry(f, show="*", width=35, font=("Sans", 14), bg=BG_COLOR, fg="white", bd=0, insertbackground="white", highlightthickness=1, highlightbackground=BUTTON_COLOR)
        self.ep.pack(pady=(10, 0), ipady=10)
        
        # Auto-login Toggle
        self.chk_autologin = tk.BooleanVar(value=True)
        tk.Checkbutton(f, text="Iniciar sesión automáticamente", variable=self.chk_autologin,
                       bg=SECONDARY_BG, fg="white", selectcolor=BG_COLOR, font=("Sans", 10)).pack(anchor="w", pady=20)
        
        nav = tk.Frame(self.main_content, bg=BG_COLOR); nav.pack(side="bottom", pady=40)
        self.btn(nav, "CANCELAR", self.root.destroy, DANGER_COLOR, width=12).pack(side="left", padx=25)
        self.btn(nav, "CREAR USUARIO", self.create, ACCENT_COLOR, width=18).pack(side="left", padx=25)

    def create(self):
        u, p = self.eu.get().strip(), self.ep.get().strip()
        if len(u) < 3 or len(p) < 4: 
            messagebox.showwarning("Error", "El nombre debe tener mín. 3 caracteres y la clave mín. 4."); return
        
        # Comprobar si el usuario existe
        try:
            subprocess.check_call(["id", "-u", u], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            messagebox.showerror("Error", f"El usuario '{u}' ya existe."); return
        except: pass

        groups = "sudo,dialout,video,input,plugdev,audio,bluetooth,lpadmin,scanner"
        subprocess.run(f"sudo useradd -m -s /bin/bash -G {groups} {u}", shell=True)
        subprocess.run(f"echo '{u}:{p}' | sudo chpasswd", shell=True)
        
        messagebox.showinfo("Éxito", f"Usuario '{u}' creado correctamente.\nYa puedes iniciar sesión con él.")
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk(); app = UserWizard(root); root.mainloop()
