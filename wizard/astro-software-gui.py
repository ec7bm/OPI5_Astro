import tkinter as tk
from tkinter import messagebox, scrolledtext
import subprocess, os, threading, shutil, sys
from PIL import Image, ImageTk
import urllib.request
import json

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
    except: return False
    except: return False

def kill_apt_locks():
    try:
        subprocess.run("sudo killall apt apt-get dpkg", shell=True, stderr=subprocess.DEVNULL)
        subprocess.run("sudo rm /var/lib/apt/lists/lock", shell=True, stderr=subprocess.DEVNULL)
        subprocess.run("sudo rm /var/cache/apt/archives/lock", shell=True, stderr=subprocess.DEVNULL)
        subprocess.run("sudo rm /var/lib/dpkg/lock*", shell=True, stderr=subprocess.DEVNULL)
        subprocess.run("sudo dpkg --configure -a", shell=True, stderr=subprocess.DEVNULL)
    except: pass
    def __init__(self, root):
        print("[DEBUG] Iniciando SoftWizard V7.0...")
        self.root = root
        self.root.title("AstroOrange Software Installer V7.0")
        self.root.geometry("900x800") # Un poco más alto para acomodar imagen grande + terminal
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
        self.clean(); self.head("Instalador Astro", "Selecciona las aplicaciones que deseas añadir")
        
        online = check_ping()
        if not online:
            tk.Label(self.main_content, text="⚠️ SIN INTERNET - CONÉCTATE PARA DESCARGAR", bg=DANGER_COLOR, fg="white", font=("Sans", 10, "bold"), padx=20, pady=5).pack(pady=5)
        
        grid = tk.Frame(self.main_content, bg=BG_COLOR); grid.pack(pady=10)
        for i, (n, info) in enumerate(SOFTWARE.items()):
            bin_name = info["bin"]
            bin_path = f"/usr/bin/{bin_name}"
            inst = bool(shutil.which(bin_name) or os.path.exists(bin_path))
            
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
        bin_path = f"/usr/bin/{bin_name}"
        if bool(shutil.which(bin_name) or os.path.exists(bin_path)):
            if self.sw_vars[name].get():
                if messagebox.askyesno("Reinstalar", f"¿Reinstalar {name}?"): self.reinstall_list.append(name)
                else: self.sw_vars[name].set(False)

    def safe_resize(self, img, size):
        try:
            return img.resize(size, Image.Resampling.LANCZOS)
        except AttributeError:
            return img.resize(size, Image.ANTIALIAS)

    def load_local_images(self):
        print(f"[DEBUG] Buscando imágenes...")
        self.carousel_images = [] 
        self.temp_nasa_files = [] 
        
        # Tamaño más grande para V7.0
        TARGET_SIZE = (500, 300)

        if check_ping():
            try:
                print("[DEBUG] Descargando 5 imágenes de NASA APOD...")
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
                                print(f"[DEBUG] ✅ NASA img {i+1} descargada")
                            except: pass
            except Exception as e:
                print(f"[DEBUG] Error descargando NASA: {e}")
        
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
            import random
            random.shuffle(self.carousel_images)
            print(f"[GALLERY] {len(self.carousel_images)} imágenes cargadas total")

    def cleanup(self):
        if self.temp_nasa_files:
            print(f"[DEBUG] Limpiando {len(self.temp_nasa_files)} archivos temporales...")
            for f in self.temp_nasa_files:
                if os.path.exists(f):
                    try: os.remove(f); print(f"[CLEAN] Borrado {f}")
                    except: pass
            self.temp_nasa_files = []

    def on_close(self):
        self.cleanup()
        self.root.destroy()
        sys.exit(0)

    def update_carousel(self):
        if hasattr(self, 'carousel_label'):
            if self.carousel_mode == "images" and self.carousel_images:
                self.carousel_label.config(image=self.carousel_images[self.carousel_index], text="")
                self.carousel_index = (self.carousel_index + 1) % len(self.carousel_images)
            else:
                emoji = CAROUSEL_EMOJIS[self.carousel_index]
                self.carousel_label.config(text=emoji, image="")
                self.carousel_index = (self.carousel_index + 1) % len(CAROUSEL_EMOJIS)
            self.root.after(3000, self.update_carousel)

    def start_install(self):
        self.clean(); self.head("Procesando...", "Instalando paquetes seleccionados")
        self.load_local_images()
        
        # Frame más alto para imagen grande (320px)
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
        # Terminal más alta (height=10)
        self.console = scrolledtext.ScrolledText(t_frm, bg="black", fg="#00ff00", font=("Monospace", 9), state="disabled", borderwidth=0, height=10)
        self.console.pack(fill="x")
        threading.Thread(target=self.run_install, daemon=True).start()

    def log(self, t):
        if self.console.winfo_exists():
            self.console.config(state="normal"); self.console.insert(tk.END, t + "\n"); self.console.see(tk.END); self.console.config(state="disabled"); self.root.update_idletasks()

    def create_shortcut(self, name, bin_name):
        try:
            # Detect real user behind sudo
            real_user = os.environ.get('SUDO_USER') or os.environ.get('USER')
            if real_user == 'root':
                # Try to guess if root (shouldn't happen with normal sudo usage)
                return

            desktop_dir = f"/home/{real_user}/Desktop"
            if not os.path.exists(desktop_dir): 
                os.makedirs(desktop_dir, exist_ok=True)
                shutil.chown(desktop_dir, user=real_user, group=real_user)

            filename = f"{bin_name}.desktop"
            path = os.path.join(desktop_dir, filename)
            
            # V10.9: Use explicit icon if available, otherwise default to bin_name
            icon_name = SOFTWARE.get(name, {}).get("icon", bin_name)
            
            with open(path, "w") as f:
                f.write(f"[Desktop Entry]\nType=Application\nName={name}\nExec={bin_name}\nIcon={icon_name}\nTerminal=false\n")
            
            os.chmod(path, 0o755)
            shutil.chown(path, user=real_user, group=real_user)
            self.log(f"✨ Icono creado en escritorio ({real_user}): {name}")
        except Exception as e:
            self.log(f"⚠️ No se pudo crear icono: {str(e)}")

    def stop_install(self):
        if self.proc and self.proc.poll() is None:
            if messagebox.askyesno("Confirmar", "¿Deseas interrumpir?"):
                self.proc.terminate(); self.log("\n>>> INSTALACIÓN INTERRUMPIDA.")
        else: self.on_close()

    def run_install(self):
        self.log("--- PREPARANDO SISTEMA (V11.2) ---")
        
        # Bucle de reintento para limpieza y actualización
        for attempt in range(1, 4):
            self.log(f"Intento {attempt}/3: Liberando bloqueos y actualizando...")
            kill_apt_locks()
            try:
                subprocess.run("sudo apt-get update", shell=True, check=True, timeout=120)
                break # Éxito
            except Exception as e:
                if attempt == 3: self.log(f"❌ Fallo persistente en update: {e}"); break
                self.log("   Reintentando en 5 segundos..."); time.sleep(5)
        
        self.log("Actualizando sistema (Upgrade parcial)...")
        try:
            env = os.environ.copy(); env['DEBIAN_FRONTEND'] = 'noninteractive'
            subprocess.run("sudo apt-get upgrade -y --no-install-recommends", shell=True, env=env, check=True)
        except Exception as e:
            self.log(f"⚠️ Nota de upgrade: {e}")

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
                if self.proc.returncode == 0: 
                    count += 1
                    self.log(f"OK: {n}")
                    self.create_shortcut(n, info['bin'])
                else: self.log(f"ERROR: {n}")
            except Exception as e: self.log(f"EXCEPCIÓN: {str(e)}")
        self.log(f"\nCOMPLETADO: {count}/{total}")
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
    
    # SYSTEM ICONS (Generic)
    icon_paths = [
        "/usr/share/icons/Papirus/32x32/apps/system-software-install.png",
        "/usr/share/icons/hicolor/48x48/apps/system-software-install.png",
        "/usr/share/icons/Papirus/32x32/categories/applications-science.png", 
        "/usr/share/pixmaps/synaptic.png"
    ]
    for p in icon_paths:
        if os.path.exists(p):
            try: root.iconphoto(False, tk.PhotoImage(file=p)); break
            except: pass
    root.mainloop()
