#!/usr/bin/env python3
import gi
import os
import subprocess
import threading
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gdk

class AstroWizard(Gtk.Window):
    def __init__(self):
        super().__init__(title="AstroOrange V2 Setup")
        self.set_border_width(20)
        self.set_default_size(800, 600)
        self.connect("destroy", Gtk.main_quit)

        # CSS Styling
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b"""
            window { background-color: #1a1b26; color: #a9b1d6; }
            button { background-color: #f7768e; color: white; padding: 10px; border-radius: 5px; font-weight: bold; }
            button:hover { background-color: #ff9e64; }
            label { font-size: 14px; }
            entry { background-color: #24283b; color: white; border: 1px solid #414868; }
            .header { font-size: 24px; font-weight: bold; color: #7aa2f7; margin-bottom: 20px; }
            .section { margin-top: 20px; margin-bottom: 10px; font-weight: bold; color: #bb9af7; }
        """)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # Main Layout
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(self.box)

        # Header
        header = Gtk.Label(label="AstroOrange V2 - Configuración Inicial")
        header.get_style_context().add_class("header")
        self.box.pack_start(header, False, False, 10)

        # Network Section
        self.add_section_header("📡 Configuración WiFi")
        self.wifi_combo = Gtk.ComboBoxText()
        self.scan_wifi()
        self.box.pack_start(self.wifi_combo, False, False, 0)
        
        self.wifi_pass = Gtk.Entry()
        self.wifi_pass.set_placeholder_text("Contraseña WiFi")
        self.wifi_pass.set_visibility(False)
        self.box.pack_start(self.wifi_pass, False, False, 0)

        # Software Section
        self.add_section_header("🔭 Software Astronómico")
        self.chk_kstars = Gtk.CheckButton(label="KStars + INDI (Completo)")
        self.chk_phd2 = Gtk.CheckButton(label="PHD2 Guiding")
        self.chk_syncthing = Gtk.CheckButton(label="Syncthing (Sincronización)")
        
        self.chk_kstars.set_active(True)
        self.chk_phd2.set_active(True)
        
        self.box.pack_start(self.chk_kstars, False, False, 0)
        self.box.pack_start(self.chk_phd2, False, False, 0)
        self.box.pack_start(self.chk_syncthing, False, False, 0)

        # Install Button
        self.btn_install = Gtk.Button(label="Instalar y Configurar")
        self.btn_install.connect("clicked", self.on_install_clicked)
        self.box.pack_end(self.btn_install, False, False, 20)

        # Log View
        self.log_view = Gtk.TextView()
        self.log_view.set_editable(False)
        self.log_view.set_wrap_mode(Gtk.WrapMode.WORD)
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_min_content_height(150)
        scrolled.add(self.log_view)
        self.box.pack_end(scrolled, True, True, 10)

    def add_section_header(self, text):
        label = Gtk.Label(label=text, xalign=0)
        label.get_style_context().add_class("section")
        self.box.pack_start(label, False, False, 5)

    def scan_wifi(self):
        try:
            # TODO: Implement real scanning
            self.wifi_combo.append_text("Escaneando...")
            self.wifi_combo.set_active(0)
            # Simulated async call (placeholder)
        except:
            pass

    def log(self, message):
        buffer = self.log_view.get_buffer()
        end_iter = buffer.get_end_iter()
        buffer.insert(end_iter, f"{message}\n")
        # Auto scroll
        adj = self.log_view.get_parent().get_vadjustment()
        adj.set_value(adj.get_upper() - adj.get_page_size())

    def on_install_clicked(self, widget):
        self.btn_install.set_sensitive(False)
        self.log("Iniciando instalación... Por favor espere.")
        
        # Start installation thread
        thread = threading.Thread(target=self.run_installation)
        thread.start()

    def run_installation(self):
        # Here we will trigger the actual bash scripts
        # For now, just simulation
        GLib.idle_add(self.log, "Configurando Red...")
        # ... logic to call bash scripts ...
        GLib.idle_add(self.log, "Instalación finalizada. Reiniciando...")
        # subprocess.call(["reboot"])

if __name__ == "__main__":
    win = AstroWizard()
    win.show_all()
    Gtk.main()
