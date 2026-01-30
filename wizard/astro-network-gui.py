import tkinter as tk
from tkinter import messagebox
import subprocess, threading

# Estilo Premium AstroOrange
BG_COLOR, SECONDARY_BG, FG_COLOR = "#0f172a", "#1e293b", "#e2e8f0"
ACCENT_COLOR, SUCCESS_COLOR, DANGER_COLOR = "#38bdf8", "#22c55e", "#ef4444"
BUTTON_COLOR = "#334155"

class NetWizard:
    def __init__(self, root):
        self.root = root
        self.root.title("AstroOrange Network Manager")
        self.root.geometry("800x650")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)
        
        self.ssid = ""
        self.main_content = tk.Frame(self.root, bg=BG_COLOR)
        self.main_content.pack(expand=True, fill="both")
        self.step_list()

    def clean(self):
        for w in self.main_content.winfo_children(): w.destroy()

    def head(self, t, s=""):
        tk.Label(self.main_content, text="📡 " + t, font=("Sans", 32, "bold"), bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=(50, 5))
        if s: tk.Label(self.main_content, text=s, font=("Sans", 14), bg=BG_COLOR, fg=FG_COLOR).pack(pady=(0, 30))

    def btn(self, parent, text, cmd, color=BUTTON_COLOR, width=18):
        return tk.Button(parent, text=text, command=cmd, bg=color, fg="white", 
                         font=("Sans", 11, "bold"), relief="flat", padx=25, pady=12, 
                         activebackground=ACCENT_COLOR, cursor="hand2", width=width)

    def step_list(self):
        self.clean(); self.head("Configuración WiFi", "Busca y conéctate a una red cercana")
        
        f = tk.Frame(self.main_content, bg=BG_COLOR); f.pack(fill="x", padx=120)
        self.lb = tk.Listbox(f, width=40, height=8, bg=SECONDARY_BG, fg="white", font=("Sans", 12), 
                             bd=0, highlightthickness=1, highlightbackground=BUTTON_COLOR, 
                             selectbackground=ACCENT_COLOR, borderwidth=10, relief="flat")
        self.lb.pack(pady=10, fill="x")
        
        tk.Button(self.main_content, text="🔄 ACTUALIZAR LISTA", command=self.scan, bg=BUTTON_COLOR, fg="white", font=("Sans",10), relief="flat", padx=20, pady=8).pack(pady=10)
        
        nav = tk.Frame(self.main_content, bg=BG_COLOR); nav.pack(side="bottom", pady=50)
        self.btn(nav, "CERRAR", self.root.destroy, DANGER_COLOR, width=12).pack(side="left", padx=25)
        self.btn(nav, "SIGUIENTE", self.step_pass, ACCENT_COLOR, width=12).pack(side="left", padx=25)
        self.scan()

    def scan(self):
        self.lb.delete(0, tk.END); self.ssids = []
        try:
            o = subprocess.check_output(["nmcli","-t","-f","SSID","dev","wifi","list"], universal_newlines=True)
            for l in o.splitlines():
                if l and l not in self.ssids: 
                    self.ssids.append(l); self.lb.insert(tk.END, f"  📶  {l}")
        except: self.lb.insert(tk.END, "No se detectaron redes WiFi")

    def step_pass(self):
        idx = self.lb.curselection()
        if not idx: messagebox.showwarning("WiFi", "Selecciona una red de la lista"); return
        self.ssid = self.ssids[idx[0]]
        
        self.clean(); self.head("Seguridad Red", f"Conectando a: {self.ssid}")
        f = tk.Frame(self.main_content, bg=SECONDARY_BG, padx=50, pady=50); f.pack(pady=20)
        tk.Label(f, text="CONTRASEÑA WIFI", bg=SECONDARY_BG, fg=ACCENT_COLOR, font=("Sans", 10, "bold")).pack(anchor="w")
        self.ep = tk.Entry(f, show="*", width=35, font=("Sans", 14), bg=BG_COLOR, fg="white", bd=0, insertbackground="white", highlightthickness=1, highlightbackground=BUTTON_COLOR)
        self.ep.pack(pady=(15, 0), ipady=10)
        
        nav = tk.Frame(self.main_content, bg=BG_COLOR); nav.pack(side="bottom", pady=50)
        self.btn(nav, "VOLVER", self.step_list, BUTTON_COLOR, width=10).pack(side="left", padx=25)
        self.btn(nav, "CONECTAR", self.connect, ACCENT_COLOR, width=15).pack(side="left", padx=25)

    def connect(self):
        pw = self.ep.get().strip(); self.clean()
        self.head("Conectando...", f"Estableciendo enlace con {self.ssid}")
        tk.Label(self.main_content, text="Por favor, espera unos segundos...", bg=BG_COLOR, fg=FG_COLOR, font=("Sans", 12)).pack(pady=30); self.root.update()
        
        def run():
            res = subprocess.run(f"sudo nmcli dev wifi connect '{self.ssid}' password '{pw}'", shell=True, capture_output=True, timeout=35)
            if res.returncode == 0:
                self.root.after(0, lambda: messagebox.showinfo("Éxito", f"Conectado correctamente a {self.ssid}"))
                self.root.after(0, self.root.destroy)
            else:
                self.root.after(0, lambda: messagebox.showerror("Error de Red", "No se pudo conectar. Verifica la contraseña.")); self.root.after(0, self.step_list)
        threading.Thread(target=run, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk(); app = NetWizard(root); root.mainloop()
