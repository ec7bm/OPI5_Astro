#!/usr/bin/env python3
"""
AstroOrange V2 - Installation Wizard
Accessible via noVNC at http://192.168.4.1:6080
"""

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Vte', '2.91')
from gi.repository import Gtk, Vte, GLib
import subprocess
import os
import sys

class AstroOrangeWizard(Gtk.Window):
    def __init__(self):
        super().__init__(title="AstroOrange Setup Wizard")
        self.set_default_size(900, 700)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        # Check if already installed
        if os.path.exists("/etc/astroorange/.installed"):
            self.show_already_installed()
            return
        
        # Create notebook for wizard pages
        self.notebook = Gtk.Notebook()
        self.notebook.set_show_tabs(False)
        self.add(self.notebook)
        
        # Data storage
        self.new_username = ""
        self.new_password = ""
        
        # Add pages (Order matters!)
        self.add_welcome_page()
        self.add_user_page()
        self.add_network_page()
        self.add_software_page()
        self.add_installation_page()
        self.add_completion_page()
        
        self.current_page = 0
        self.selected_software = []
        
    def show_already_installed(self):
        """Show message if system is already configured"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        box.set_margin_top(200)
        box.set_margin_start(50)
        box.set_margin_end(50)
        
        label = Gtk.Label()
        label.set_markup("<span size='xx-large'><b>AstroOrange Already Configured</b></span>")
        box.pack_start(label, False, False, 0)
        
        info = Gtk.Label(label="Your system has already been set up.\nYou can close this window.")
        box.pack_start(info, False, False, 0)
        
        close_btn = Gtk.Button(label="Close")
        close_btn.connect("clicked", Gtk.main_quit)
        box.pack_start(close_btn, False, False, 0)
        
        self.add(box)
        
    def add_welcome_page(self):
        """Welcome screen"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        box.set_margin_top(100)
        box.set_margin_start(50)
        box.set_margin_end(50)
        
        # Title
        title = Gtk.Label()
        title.set_markup("<span size='xx-large'><b>Welcome to AstroOrange</b></span>")
        box.pack_start(title, False, False, 0)
        
        # Description
        desc = Gtk.Label(label="Professional Astronomical Linux Distribution\n\n"
                              "This wizard will help you:\n"
                              "• Create your system user\n"
                              "• Configure your network\n"
                              "• Install astronomical software\n\n"
                              "Click 'Next' to begin.")
        box.pack_start(desc, False, False, 0)
        
        # Next button
        next_btn = Gtk.Button(label="Next →")
        next_btn.connect("clicked", self.next_page)
        box.pack_end(next_btn, False, False, 0)
        
        self.notebook.append_page(box, Gtk.Label(label="Welcome"))

    def add_user_page(self):
        """User Creation Screen"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        box.set_margin_top(50)
        box.set_margin_start(50)
        box.set_margin_end(50)
        
        title = Gtk.Label()
        title.set_markup("<span size='x-large'><b>Create User</b></span>")
        box.pack_start(title, False, False, 0)
        
        info = Gtk.Label(label="Set the username and password for system access (Desktop/VNC).")
        box.pack_start(info, False, False, 0)
        
        # Grid for inputs
        grid = Gtk.Grid()
        grid.set_column_spacing(10)
        grid.set_row_spacing(10)
        grid.set_halign(Gtk.Align.CENTER)
        
        grid.attach(Gtk.Label(label="Username:"), 0, 0, 1, 1)
        self.user_entry = Gtk.Entry()
        self.user_entry.set_text("astro")
        grid.attach(self.user_entry, 1, 0, 1, 1)
        
        grid.attach(Gtk.Label(label="Password:"), 0, 1, 1, 1)
        self.pass_entry = Gtk.Entry()
        self.pass_entry.set_visibility(False)
        grid.attach(self.pass_entry, 1, 1, 1, 1)
        
        box.pack_start(grid, False, False, 0)
        
        # Navigation
        btn_box = Gtk.Box(spacing=10)
        back_btn = Gtk.Button(label="← Back")
        back_btn.connect("clicked", self.prev_page)
        btn_box.pack_start(back_btn, False, False, 0)
        
        next_btn = Gtk.Button(label="Next →")
        next_btn.connect("clicked", self.validate_user_page)
        btn_box.pack_end(next_btn, False, False, 0)
        
        box.pack_end(btn_box, False, False, 0)
        
        self.notebook.append_page(box, Gtk.Label(label="User"))

    def validate_user_page(self, widget):
        """Validate and create user"""
        user = self.user_entry.get_text()
        passwd = self.pass_entry.get_text()
        
        if not user or not passwd:
            # Simple error handling via dialog or visual cue
            return
            
        self.new_username = user
        self.new_password = passwd
        
        # Execute user creation immediately or queue it?
        # Doing it immediately ensures subsequent steps (running scripts) 
        # *could* theoretically use it, but our scripts run as sudo/root invoked by main.py.
        # Let's create it in background now.
        try:
            # Create user if not exists
            subprocess.run(["sudo", "useradd", "-m", "-s", "/bin/bash", "-G", "sudo,video,dialout,plugdev", user], check=False)
            # Set password
            p = subprocess.Popen(["sudo", "chpasswd"], stdin=subprocess.PIPE)
            p.communicate(input=f"{user}:{passwd}".encode())
            
            # Setup VNC for this new user too?
            # Ideally yes, so they can log in later.
            vnc_dir = f"/home/{user}/.vnc"
            subprocess.run(["sudo", "mkdir", "-p", vnc_dir])
            p_vnc = subprocess.Popen(["sudo", "vncpasswd", "-f"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            out, _ = p_vnc.communicate(input=f"{passwd}\n{passwd}".encode()) # Use same pass for VNC
            
            # Write passwd file
            with open("/tmp/vncpasswd", "wb") as f:
                f.write(out)
            subprocess.run(["sudo", "mv", "/tmp/vncpasswd", f"{vnc_dir}/passwd"])
            subprocess.run(["sudo", "chown", "-R", f"{user}:{user}", f"/home/{user}"])
            subprocess.run(["sudo", "chmod", "600", f"{vnc_dir}/passwd"])
            
        except Exception as e:
            print(f"Error creating user: {e}")
            
        self.next_page(widget)

    def add_network_page(self):
        """Network Screen"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        box.set_margin_top(50)
        box.set_margin_start(50)
        box.set_margin_end(50)
        
        title = Gtk.Label()
        title.set_markup("<span size='x-large'><b>Network Configuration</b></span>")
        box.pack_start(title, False, False, 0)
        
        status_label = Gtk.Label(label="Checking network status...")
        box.pack_start(status_label, False, False, 0)
        
        info = Gtk.Label(label="You are currently connected. If you are in Hotspot mode,\n"
                              "you can configure WiFi now to get internet access.")
        box.pack_start(info, False, False, 0)
        
        wifi_btn = Gtk.Button(label="Configure WiFi (nmtui)")
        wifi_btn.connect("clicked", self.configure_wifi)
        box.pack_start(wifi_btn, False, False, 0)
        
        btn_box = Gtk.Box(spacing=10)
        back_btn = Gtk.Button(label="← Back")
        back_btn.connect("clicked", self.prev_page)
        btn_box.pack_start(back_btn, False, False, 0)
        
        skip_btn = Gtk.Button(label="Skip / Continue →")
        skip_btn.connect("clicked", self.next_page)
        btn_box.pack_end(skip_btn, False, False, 0)
        
        box.pack_end(btn_box, False, False, 0)
        
        self.notebook.append_page(box, Gtk.Label(label="Network"))
        
    def add_software_page(self):
        """Software Selection Screen"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        box.set_margin_top(50)
        box.set_margin_start(50)
        box.set_margin_end(50)
        
        title = Gtk.Label()
        title.set_markup("<span size='x-large'><b>Select Software</b></span>")
        box.pack_start(title, False, False, 0)
        
        info = Gtk.Label(label="Choose the astronomical software to install:")
        box.pack_start(info, False, False, 0)
        
        self.software_checks = {}
        # ID, Name, Description
        software_list = [
            ("kstars", "KStars + INDI", "Planetarium and telescope control"),
            ("phd2", "PHD2", "Autoguiding software"),
            ("astrodmx", "AstroDMX Capture", "Imaging capture (Linux/ARM)"),
            ("astap", "ASTAP", "Plate Solving & Stacking"),
            ("stellarium", "Stellarium", "Visual Planetarium"),
            ("ccdciel", "CCDciel", "CCD Capture Software"),
            ("syncthing", "Syncthing", "File Synchronization"),
        ]
        
        for sw_id, sw_name, sw_desc in software_list:
            check = Gtk.CheckButton(label=f"{sw_name} - {sw_desc}")
            # Default selections
            check.set_active(sw_id in ["kstars", "phd2", "astap"]) 
            self.software_checks[sw_id] = check
            box.pack_start(check, False, False, 0)
        
        btn_box = Gtk.Box(spacing=10)
        back_btn = Gtk.Button(label="← Back")
        back_btn.connect("clicked", self.prev_page)
        btn_box.pack_start(back_btn, False, False, 0)
        
        next_btn = Gtk.Button(label="Install →")
        next_btn.connect("clicked", self.start_installation)
        btn_box.pack_end(next_btn, False, False, 0)
        
        box.pack_end(btn_box, False, False, 0)
        
        self.notebook.append_page(box, Gtk.Label(label="Software"))
        
    def add_installation_page(self):
        """Installation Screen"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        box.set_margin_top(50)
        box.set_margin_start(50)
        box.set_margin_end(50)
        
        title = Gtk.Label()
        title.set_markup("<span size='x-large'><b>Installing...</b></span>")
        box.pack_start(title, False, False, 0)
        
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_show_text(True)
        box.pack_start(self.progress_bar, False, False, 0)
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        self.terminal = Vte.Terminal()
        scrolled.add(self.terminal)
        box.pack_start(scrolled, True, True, 0)
        
        self.notebook.append_page(box, Gtk.Label(label="Installation"))
        
    def add_completion_page(self):
        """Completion Screen"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        box.set_margin_top(100)
        box.set_margin_start(50)
        box.set_margin_end(50)
        
        title = Gtk.Label()
        title.set_markup("<span size='xx-large'><b>Installation Complete!</b></span>")
        box.pack_start(title, False, False, 0)
        
        info = Gtk.Label(label="AstroOrange has been successfully configured.\n\n"
                              "Access Information:\n"
                              "• Web VNC: https://<IP>:6080\n"
                              "• Syncthing: http://<IP>:8384\n\n"
                              "The system will reboot in 10 seconds...")
        box.pack_start(info, False, False, 0)
        
        reboot_btn = Gtk.Button(label="Reboot Now")
        reboot_btn.connect("clicked", self.reboot_system)
        box.pack_start(reboot_btn, False, False, 0)
        
        self.notebook.append_page(box, Gtk.Label(label="Complete"))
        
    def next_page(self, widget):
        self.current_page += 1
        self.notebook.set_current_page(self.current_page)
        
    def prev_page(self, widget):
        self.current_page -= 1
        self.notebook.set_current_page(self.current_page)
        
    def configure_wifi(self, widget):
        subprocess.Popen(["x-terminal-emulator", "-e", "sudo nmtui"])
        
    def start_installation(self, widget):
        self.next_page(widget)
        self.selected_software = [sw_id for sw_id, check in self.software_checks.items() if check.get_active()]
        GLib.idle_add(self.run_installation)
        
    def run_installation(self):
        total = len(self.selected_software)
        for i, software in enumerate(self.selected_software):
            progress = (i + 1) / total
            self.progress_bar.set_fraction(progress)
            self.progress_bar.set_text(f"Installing {software}... ({i+1}/{total})")
            
            script = f"/usr/local/bin/install-{software}.sh"
            if os.path.exists(script):
                # Pass the new username to scripts if needed?
                # For now scripts assume current user or system wide.
                # Scripts like 'install-kstars.sh' use 'whoami'. 
                # Since wizard runs as root (via sudo), 'whoami' is root.
                # We need to target the NEW user for group addition.
                # FIX: Pass username as argument to scripts.
                
                env = os.environ.copy()
                env["TARGET_USER"] = self.new_username if self.new_username else "orangepi"
                
                self.terminal.spawn_sync(
                    Vte.PtyFlags.DEFAULT,
                    os.environ['HOME'],
                    ["/bin/bash", script],
                    [], # env vars not passed easily here in pyobject Gtk3 without full env map?
                        # Actually spawn_sync takes env names? No, it takes argv.
                        # Easier: export var in bash call
                    GLib.SpawnFlags.DO_NOT_REAP_CHILD,
                    None,
                    None,
                )
                
                # Manual fix for group addition since scripts might use 'whoami'
                subprocess.run(["sudo", "usermod", "-a", "-G", "dialout,video,plugdev", self.new_username], check=False)

        os.makedirs("/etc/astroorange", exist_ok=True)
        open("/etc/astroorange/.installed", "w").close()
        self.next_page(None)
        GLib.timeout_add_seconds(10, self.reboot_system, None)
        return False
        
    def reboot_system(self, widget):
        subprocess.run(["sudo", "reboot"])
        Gtk.main_quit()

def main():
    win = AstroOrangeWizard()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
