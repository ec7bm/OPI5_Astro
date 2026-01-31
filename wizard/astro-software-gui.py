import tkinter as tk
from tkinter import messagebox, scrolledtext
import subprocess, os, threading, shutil, sys

# --- CONFIGURACIÓN ESTÉTICA PREMIUM ---
BG_COLOR, SECONDARY_BG, FG_COLOR = "#0f172a", "#1e293b", "#e2e8f0"
ACCENT_COLOR, SUCCESS_COLOR, DANGER_COLOR = "#38bdf8", "#22c55e", "#ef4444"
BUTTON_COLOR = "#334155"

SOFTWARE = {
    "KStars / INDI": {"bin": "kstars", "pkg": "kstars-bleeding indi-full gsc", "ppa": "ppa:mutlaqja/ppa"},
    "PHD2 Guiding": {"bin": "phd2", "pkg": "phd2", "ppa": "ppa:pch/phd2"},
    "ASTAP (Solver)": {"bin": "astap", "pkg": "astap", "url": "https://www.hnsky.org/astap_arm64.deb"},
    "Stellarium": {"bin": "stellarium", "pkg": "stellarium"},
    "AstroDMX Capture": {"bin": "astrodmx", "pkg": "astrodmxcapture", "url": "https://www.astrodmx.com/download/astrodmxcapture-release.deb"},
    "CCDciel": {"bin": "ccdciel", "pkg": "ccdciel", "ppa": "ppa:jandecaluwe/ccdciel"},
    "Syncthing": {"bin": "syncthing", "pkg": "syncthing"}
}

def check_ping():
    try:
        subprocess.check_output(["ping", "-c", "1", "-W", "1", "8.8.8.8"])
        return True
    except: return False

class SoftWizard:
    def __init__(self, root):
        self.root = root
        self.root.title("AstroOrange Software Installer")
        self.root.geometry("900x750")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)
        
        self.sw_vars = {}
        self.reinstall_list = []
        self.proc = None
        
        self.main_content = tk.Frame(self.root, bg=BG_COLOR)
        self.main_content.pack(expand=True, fill="both")
        
        self.draw_main()

    def clean(self):
        for w in self.main_content.winfo_children(): w.destroy()

    def head(self, t, s=""):
        tk.Label(self.main_content, text="🔭 " + t, font=("Sans", 32, "bold"), bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=(60, 5))
        if s: tk.Label(self.main_content, text=s, font=("Sans", 14), bg=BG_COLOR, fg=FG_COLOR).pack(pady=(0, 40))

    def btn(self, text, cmd, color=BUTTON_COLOR, width=20, bold=True):
        f = "bold" if bold else "normal"
        return tk.Button(self.main_content, text=text, command=cmd, bg=color, fg="white", 
                         font=("Sans", 11, f), relief="flat", padx=20, pady=10, 
                         activebackground=ACCENT_COLOR, cursor="hand2", width=width)

    def draw_main(self):
        self.clean(); self.head("Instalador Astro", "Selecciona las aplicaciones que deseas añadir")
        
        online = check_ping()
        if not online:
            tk.Label(self.main_content, text="⚠️ SIN INTERNET - CONÉCTATE PARA DESCARGAR", bg=DANGER_COLOR, fg="white", font=("Sans", 10, "bold"), padx=20, pady=5).pack(pady=5)
        
        grid = tk.Frame(self.main_content, bg=BG_COLOR); grid.pack(pady=10)
        for i, (n, info) in enumerate(SOFTWARE.items()):
            inst = bool(shutil.which(info["bin"]) or os.path.exists(f"/usr/bin/{info['bin']}"))
            self.sw_vars[n] = tk.BooleanVar(value=not inst and n in ["KStars / INDI", "PHD2 Guiding"])
            txt = n + (" (INSTALADO)" if inst else "")
            cb = tk.Checkbutton(grid, text=txt, variable=self.sw_vars[n], bg=SECONDARY_BG, fg="white", 
                               selectcolor=ACCENT_COLOR, font=("Sans", 11, "bold"), padx=25, pady=12, 
                               indicatoron=False, width=25, command=lambda name=n: self.on_sw_click(name))
            cb.grid(row=i//2, column=i%2, padx=12, pady=12, sticky="ew")
            
        self.btn("🚀 INICIAR INSTALACIÓN", self.start_install, ACCENT_COLOR, width=40).pack(pady=30)
        
        ctrl = tk.Frame(self.main_content, bg=BG_COLOR); ctrl.pack()
        tk.Button(ctrl, text="SALIR", command=self.root.destroy, bg=BUTTON_COLOR, fg="white", font=("Sans",11), relief="flat", padx=30, pady=8).pack()

    def on_sw_click(self, name):
        if bool(shutil.which(SOFTWARE[name]["bin"]) or os.path.exists(f"/usr/bin/{SOFTWARE[name]['bin']}")):
            if self.sw_vars[name].get():
                if messagebox.askyesno("Reinstalar", f"¿Reinstalar {name}?"): self.reinstall_list.append(name)
                else: self.sw_vars[name].set(False)

    def start_install(self):
        self.clean(); self.head("Procesando...", "Instalando paquetes seleccionados")
        
        self.cancel_btn = tk.Button(self.main_content, text="ABORTAR INSTALACIÓN", command=self.stop_install, bg=DANGER_COLOR, fg="white", font=("Sans",11,"bold"), relief="flat", padx=25, pady=10)
        self.cancel_btn.pack(pady=20)
        
        t_frm = tk.Frame(self.main_content, bg="black", bd=2); t_frm.pack(fill="both", expand=True, padx=50, pady=10)
        self.console = scrolledtext.ScrolledText(t_frm, bg="black", fg="#00ff00", font=("Monospace", 10), state="disabled", borderwidth=0)
        self.console.pack(fill="both", expand=True)
        threading.Thread(target=self.run_install, daemon=True).start()

    def log(self, t):
        if self.console.winfo_exists():
            self.console.config(state="normal"); self.console.insert(tk.END, t + "\n"); self.console.see(tk.END); self.console.config(state="disabled"); self.root.update_idletasks()

    def stop_install(self):
        if self.proc and self.proc.poll() is None:
            if messagebox.askyesno("Confirmar", "¿Deseas interrumpir?"):
                self.proc.terminate(); self.log("\n>>> INSTALACIÓN INTERRUMPIDA.")
        else: self.root.destroy()

    def run_install(self):
        subprocess.run("sudo apt-get update", shell=True)
        count = 0; total = sum(1 for v in self.sw_vars.values() if v.get())
        for n, info in SOFTWARE.items():
            if not self.sw_vars[n].get(): continue
            try:
                self.log(f"--- INSTALANDO: {n} ---")
                if "url" in info:
                    subprocess.run(f"sudo wget -O /tmp/temp.deb {info['url']}", shell=True); cmd = "sudo dpkg -i /tmp/temp.deb || sudo apt-get install -f -y"
                else:
                    if info.get('ppa'): subprocess.run(f"sudo add-apt-repository -y {info['ppa']}", shell=True)
                    f = "--reinstall" if n in self.reinstall_list else ""; cmd = f"sudo apt-get install -y {f} {info['pkg']}"
                
                self.proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                for line in self.proc.stdout: self.log(line.strip())
                self.proc.wait()
                if self.proc.returncode == 0: count += 1; self.log(f"OK: {n}")
                else: self.log(f"ERROR: {n}")
            except Exception as e: self.log(f"EXCEPCIÓN: {str(e)}")
        
        self.log(f"\nCOMPLETADO: {count}/{total}")
        self.cancel_btn.config(text="CERRAR Y FINALIZAR", bg=SUCCESS_COLOR, command=self.root.destroy)

    def center_window(self):
        self.root.update_idletasks()
        w, h = self.root.winfo_width(), self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"+{x}+{y}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SoftWizard(root)
    app.center_window()
    try: 
        img = tk.PhotoImage(file="/usr/share/icons/Papirus/32x32/apps/kstars.png")
        root.iconphoto(False, img)
    except: pass
    root.mainloop()
