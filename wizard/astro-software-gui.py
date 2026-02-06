import tkinter as tk
from tkinter import messagebox, scrolledtext
import subprocess, os, threading, shutil, sys, time
from PIL import Image, ImageTk
import urllib.request
import json
import random

# --- CONFIGURACIÓN ESTÉTICA PREMIUM ---
BG_COLOR, SECONDARY_BG, FG_COLOR = "#0f172a", "#1e293b", "#e2e8f0"
ACCENT_COLOR, SUCCESS_COLOR, DANGER_COLOR = "#38bdf8", "#22c55e", "#ef4444"
BUTTON_COLOR = "#334155"

SOFTWARE = {
    "KStars / INDI": {"bin": "kstars", "pkg": "kstars-bleeding indi-full gsc", "ppa": "ppa:mutlaqja/ppa", "icon": "kstars"},
    "PHD2 Guiding": {"bin": "phd2", "pkg": "phd2", "ppa": "ppa:pch/phd2", "icon": "phd2"},
    "ASTAP (Solver)": {"bin": "astap", "pkg": "astap", "url": "https://www.hnsky.org/astap_arm64.deb", "icon": "astap"},
    "Stellarium": {"bin": "stellarium", "pkg": "stellarium", "icon": "stellarium"},
    "AstroDMX Capture": {"bin": "astrodmx", "pkg": "astrodmxcapture", "url": "https://www.astrodmx.com/download/astrodmxcapture-release.deb", "icon": "astrodmx"},
    "CCDciel": {"bin": "ccdciel", "pkg": "ccdciel", "ppa": "ppa:jandecaluwe/ccdciel", "icon": "ccdciel"},
    "Syncthing": {"bin": "usr/bin/syncthing", "pkg": "syncthing", "icon": "syncthing"}
}

CAROUSEL_EMOJIS = ["🔭", "🌌", "⭐", "🪐", "🌠"]

def check_ping():
    try:
        subprocess.check_output(["ping", "-c", "1", "-W", "1", "8.8.8.8"])
        return True
    except:
        return False

def kill_apt_locks():
    try:
        # 1. Detener servicios automáticos que suelen bloquear apt
        subprocess.run("sudo systemctl stop apt-daily.service apt-daily-upgrade.service 2>/dev/null", shell=True)
        
        # 2. Matar procesos conflictivos (incluyendo packagekitd)
        subprocess.run("sudo killall -9 apt apt-get dpkg packagekitd 2>/dev/null", shell=True)
        time.sleep(2)
        
        # 3. Forzar liberación de archivos de bloqueo con fuser (si existe) y rm
        lock_files = [
            "/var/lib/apt/lists/lock",
            "/var/cache/apt/archives/lock",
            "/var/lib/dpkg/lock",
            "/var/lib/dpkg/lock-frontend",
            "/var/lib/dpkg/lock-vnc"
        ]
        for f in lock_files:
            if os.path.exists(f):
                subprocess.run(f"sudo fuser -k {f} 2>/dev/null", shell=True)
                subprocess.run(f"sudo rm -f {f}", shell=True)
            
        # 4. Reparar dpkg de forma NO INTERACTIVA y con timeout
        env = os.environ.copy()
        env['DEBIAN_FRONTEND'] = 'noninteractive'
        subprocess.run("sudo dpkg --configure -a", shell=True, env=env, timeout=60)
        
        # 5. Reparar dependencias rotas y limpiar (V11.10 aggressive)
        subprocess.run("sudo apt-get install -y --fix-broken --fix-missing", shell=True, env=env, timeout=120)
        
        # 6. Asegurar repositorios estándar habilitados (V11.12)
        subprocess.run("sudo add-apt-repository -y universe", shell=True, env=env)
        subprocess.run("sudo add-apt-repository -y multiverse", shell=True, env=env)
        
        subprocess.run("sudo apt-get autoremove -y", shell=True, env=env, timeout=60)
        subprocess.run("sudo apt-get clean", shell=True, env=env, timeout=30)
    except Exception as e:
        print(f"[DEBUG] kill_apt_locks error: {e}")




class SoftWizard:

    def __init__(self, root):
        self.root = root
        self.root.title("AstroOrange Software Installer V11.6.2")
        self.root.geometry("900x800")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)
        
        self.sw_vars = {}
        self.reinstall_list = []
        self.proc = None
        self.carousel_index = 0
        self.carousel_images = []
        self.carousel_mode = "emoji"
        self.temp_nasa_files = [] 
        
        self.wizard_dir = os.path.dirname(os.path.abspath(__file__))
        self.gallery_dir = os.path.join(self.wizard_dir, "gallery")
        
        self.main_content = tk.Frame(self.root, bg=BG_COLOR)
        self.main_content.pack(expand=True, fill="both")
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.center_window()
        self.draw_main()


    def clean(self):
        for w in self.main_content.winfo_children(): w.destroy()

    def head(self, t, s=""):
        tk.Label(self.main_content, text="🔭 " + t, font=("Sans", 32, "bold"), bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=(20, 5))
        if s: tk.Label(self.main_content, text=s, font=("Sans", 14), bg=BG_COLOR, fg=FG_COLOR).pack(pady=(0, 10))

    def btn(self, text, cmd, color=BUTTON_COLOR, width=20, bold=True):
        f = "bold" if bold else "normal"
        return tk.Button(self.main_content, text=text, command=cmd, bg=color, fg="white", 
                         font=("Sans", 11, f), relief="flat", padx=20, pady=10, 
                         activebackground=ACCENT_COLOR, cursor="hand2", width=width)

    def draw_main(self):
        self.clean()
        self.head("Instalador Astro", "Selecciona las aplicaciones que deseas añadir")
        
        online = check_ping()
        if not online:
            tk.Label(self.main_content, text="⚠️ SIN INTERNET - CONÉCTATE PARA DESCARGAR", bg=DANGER_COLOR, fg="white", font=("Sans", 10, "bold"), padx=20, pady=5).pack(pady=5)
        
        grid = tk.Frame(self.main_content, bg=BG_COLOR); grid.pack(pady=10)
        for i, (n, info) in enumerate(SOFTWARE.items()):
            bin_name = info["bin"]
            inst = bool(shutil.which(bin_name) or os.path.exists(f"/usr/bin/{bin_name}"))
            
            self.sw_vars[n] = tk.BooleanVar(value=not inst and n in ["KStars / INDI", "PHD2 Guiding"])
            txt = n + (" (INSTALADO)" if inst else "")
            cb = tk.Checkbutton(grid, text=txt, variable=self.sw_vars[n], bg=SECONDARY_BG, fg="white", 
                               selectcolor=ACCENT_COLOR, font=("Sans", 11, "bold"), padx=25, pady=12, 
                               indicatoron=False, width=25, command=lambda name=n: self.on_sw_click(name))
            cb.grid(row=i//2, column=i%2, padx=12, pady=12, sticky="ew")
            
        self.btn("🚀 INICIAR INSTALACIÓN", self.start_install, ACCENT_COLOR, width=40).pack(pady=30)
        
        ctrl = tk.Frame(self.main_content, bg=BG_COLOR); ctrl.pack()
        tk.Button(ctrl, text="SALIR", command=self.on_close, bg=BUTTON_COLOR, fg="white", font=("Sans",11), relief="flat", padx=30, pady=8).pack()

    def on_sw_click(self, name):
        bin_name = SOFTWARE[name]["bin"]
        if bool(shutil.which(bin_name) or os.path.exists(f"/usr/bin/{bin_name}")):
            if self.sw_vars[name].get():
                if messagebox.askyesno("Reinstalar", f"¿Reinstalar {name}?"): self.reinstall_list.append(name)
                else: self.sw_vars[name].set(False)

    def safe_resize(self, img, size):
        try:
            return img.resize(size, Image.Resampling.LANCZOS)
        except AttributeError:
            return img.resize(size, Image.ANTIALIAS)

    def load_local_images(self):
        self.carousel_images = [] 
        self.temp_nasa_files = [] 
        TARGET_SIZE = (500, 300)

        if check_ping():
            try:
                url = "https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY&count=5"
                with urllib.request.urlopen(url, timeout=5) as response:
                    data = json.loads(response.read().decode())
                    for i, item in enumerate(data):
                        if item.get('media_type') == 'image':
                            img_url = item.get('url')
                            nasa_path = f"/tmp/nasa_apod_{i}.jpg"
                            urllib.request.urlretrieve(img_url, nasa_path)
                            self.temp_nasa_files.append(nasa_path)
                            try:
                                img = Image.open(nasa_path)
                                img = self.safe_resize(img, TARGET_SIZE)
                                photo = ImageTk.PhotoImage(img)
                                self.carousel_images.append(photo)
                            except: pass
            except: pass
        
        image_files = ["andromeda.png", "spiral_galaxy.png", "carina_nebula.png", "orion_nebula.png", "pillars.png"]
        if os.path.exists(self.gallery_dir):
            for img_file in image_files:
                img_path = os.path.join(self.gallery_dir, img_file)
                if os.path.exists(img_path):
                    try:
                        img = Image.open(img_path)
                        img = self.safe_resize(img, TARGET_SIZE)
                        photo = ImageTk.PhotoImage(img)
                        self.carousel_images.append(photo)
                    except: pass
        
        if self.carousel_images:
            self.carousel_mode = "images"
            random.shuffle(self.carousel_images)

    def cleanup(self):
        for f in self.temp_nasa_files:
            if os.path.exists(f):
                try: os.remove(f)
                except: pass
        self.temp_nasa_files = []

    def on_close(self):
        self.cleanup()
        self.root.destroy()
        sys.exit(0)

    def update_carousel(self):
        if hasattr(self, 'carousel_label') and self.carousel_label.winfo_exists():
            if self.carousel_mode == "images" and self.carousel_images:
                self.carousel_label.config(image=self.carousel_images[self.carousel_index], text="")
                self.carousel_index = (self.carousel_index + 1) % len(self.carousel_images)
            else:
                emoji = CAROUSEL_EMOJIS[self.carousel_index]
                self.carousel_label.config(text=emoji, image="")
                self.carousel_index = (self.carousel_index + 1) % len(CAROUSEL_EMOJIS)
            self.root.after(3000, self.update_carousel)

    def start_install(self):
        self.clean()
        self.head("Procesando...", "Instalando paquetes seleccionados")
        self.load_local_images()
        
        carousel_frame = tk.Frame(self.main_content, bg=BG_COLOR, height=320)
        carousel_frame.pack(pady=10)
        
        if self.carousel_mode == "images" and self.carousel_images:
            self.carousel_label = tk.Label(carousel_frame, image=self.carousel_images[0], bg=BG_COLOR)
        else:
            self.carousel_label = tk.Label(carousel_frame, text=CAROUSEL_EMOJIS[0], font=("Sans", 72), bg=BG_COLOR, fg=ACCENT_COLOR)
        
        self.carousel_label.pack()
        self.update_carousel()
        
        self.cancel_btn = tk.Button(self.main_content, text="ABORTAR INSTALACIÓN", command=self.stop_install, bg=DANGER_COLOR, fg="white", font=("Sans",11,"bold"), relief="flat", padx=25, pady=10)
        self.cancel_btn.pack(pady=10)
        
        t_frm = tk.Frame(self.main_content, bg="black", bd=2)
        t_frm.pack(fill="x", padx=50, pady=10)
        self.console = scrolledtext.ScrolledText(t_frm, bg="black", fg="#00ff00", font=("Monospace", 9), state="disabled", borderwidth=0, height=10)
        self.console.pack(fill="x")
        threading.Thread(target=self.run_install, daemon=True).start()

    def log(self, t):
        if hasattr(self, 'console') and self.console.winfo_exists():
            self.console.config(state="normal")
            self.console.insert(tk.END, t + "\n")
            self.console.see(tk.END)
            self.console.config(state="disabled")
            self.root.update_idletasks()

    def create_shortcut(self, name, bin_name):
        try:
            real_user = os.environ.get('SUDO_USER') or os.environ.get('USER')
            if real_user == 'root': return
            desktop_dir = f"/home/{real_user}/Desktop"
            if not os.path.exists(desktop_dir): 
                os.makedirs(desktop_dir, exist_ok=True)
                shutil.chown(desktop_dir, user=real_user, group=real_user)
            filename = f"{bin_name}.desktop"
            path = os.path.join(desktop_dir, filename)
            icon_name = SOFTWARE.get(name, {}).get("icon", bin_name)
            with open(path, "w") as f:
                f.write(f"[Desktop Entry]\nType=Application\nName={name}\nExec={bin_name}\nIcon={icon_name}\nTerminal=false\n")
            os.chmod(path, 0o755)
            shutil.chown(path, user=real_user, group=real_user)
            self.log(f"✨ Icono creado: {name}")
        except Exception as e:
            self.log(f"⚠️ Error icono: {str(e)}")

    def stop_install(self):
        if self.proc and self.proc.poll() is None:
            if messagebox.askyesno("Confirmar", "¿Deseas interrumpir?"):
                self.proc.terminate()
                self.log("\n>>> INSTALACIÓN INTERRUMPIDA.")
        else:
            self.on_close()

    def run_install(self):
        self.log("--- PREPARANDO SISTEMA ---")
        for attempt in range(1, 4):
            self.log(f"Intento {attempt}/3: Liberando bloqueos...")
            kill_apt_locks()
            try:
                subprocess.run("sudo apt-get update", shell=True, check=True, timeout=120)
                break
            except:
                if attempt == 3: self.log("❌ Fallo persistente en update"); break
                time.sleep(5)
        
        self.log("Sincronizando librerías base (Alineación v11.11)...")
        try:
            env = os.environ.copy(); env['DEBIAN_FRONTEND'] = 'noninteractive'
            # Forzar actualización de paquetes base conflictivos de Jammy
            self.log("   Corrigiendo gcc-11-base...")
            subprocess.run("sudo apt-get install -y --only-upgrade gcc-11-base libgcc-s1", shell=True, env=env)
            self.log("   Ejecutando dist-upgrade...")
            subprocess.run("sudo apt-get dist-upgrade -y --no-install-recommends", shell=True, env=env, check=True)
        except Exception as e:
            self.log(f"⚠️ Nota de upgrade: {e}")



        for n, info in SOFTWARE.items():
            if not self.sw_vars[n].get(): continue
            try:
                self.log(f"--- INSTALANDO: {n} ---")
                if "url" in info:
                    subprocess.run(f"sudo wget -O /tmp/temp.deb {info['url']}", shell=True)
                    cmd = "sudo dpkg -i /tmp/temp.deb || sudo apt-get install -f -y"
                else:
                    if info.get('ppa'): 
                        self.log(f"   Añadiendo repositorio {info['ppa']}...")
                        res = subprocess.Popen(f"sudo add-apt-repository -y {info['ppa']}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                        if res.stdout:
                            for line in res.stdout: self.log(f"      {line.strip()}")
                        res.wait()
                        self.log("   Actualizando lista de paquetes...")
                        subprocess.run("sudo apt-get update", shell=True)
                    
                    f = "--reinstall" if n in self.reinstall_list else ""
                    cmd = f"sudo apt-get install -y {f} {info['pkg']}"


                self.proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                for line in self.proc.stdout: self.log(line.strip())
                self.proc.wait()
                if self.proc.returncode == 0: 
                    self.create_shortcut(n, info['bin'])
                    self.log(f"OK: {n}")
                else:
                    self.log(f"ERROR: {n}")
            except Exception as e:
                self.log(f"EXCEPCIÓN: {str(e)}")
        
        self.cancel_btn.config(text="CERRAR Y FINALIZAR", bg=SUCCESS_COLOR, command=self.on_close)

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
    root.mainloop()
