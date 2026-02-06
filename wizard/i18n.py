import os

LANG_FILE = "/etc/astroorange/language.conf"

TRANSLATIONS = {
    "es": {
        "welcome": "¡Bienvenido a AstroOrange!",
        "setup_panel": "Panel de Configuración",
        "recommended": "Recomendado para empezar:",
        "start_tutorial": "INICIAR TUTORIAL COMPLETO",
        "tools": "Herramientas Individuales:",
        "config_user": "Configurar Usuario",
        "config_wifi": "Configurar Red WiFi",
        "install_soft": "Instalar Software",
        "no_more_show": "No mostrar este panel al iniciar sesión",
        "setup_done_msg": "El asistente ya no se mostrará automáticamente.",
        "tutorial_complete": "¡Configuración completada!",
        "ask_wifi": "¿Deseas configurar WiFi?",
        "ask_software": "¿Deseas instalar software?",
        "exit": "SALIR",
        "abort": "ABORTAR INSTALACIÓN",
        "installed": "INSTALADO",
        "start_install": "INICIAR INSTALACIÓN",
        "processing": "Procesando...",
        "installing_pkgs": "Instalando paquetes seleccionados",
        "restart_wizard": "REINICIAR WIZARD PARA VER CAMBIOS",
        "critical_error": "ERROR CRÍTICO",
        "fatal_error": "Error Fatal",
        "next": "SIGUIENTE",
        "back": "ATRÁS",
        "finish": "FINALIZAR",
        "user_manager": "Gestor de Usuarios",
        "create_user": "Crear Usuario",
        "username": "Nombre de usuario:",
        "password": "Contraseña:",
        "confirm_password": "Confirmar contraseña:",
        "autologin": "Inicio de sesión automático",
        "network_manager": "Gestor de Red",
        "scanning": "Escaneando...",
        "connect": "CONECTAR",
        "password_required": "Contraseña requerida",
        "manual_connect": "Conexión Manual",
        "select_language": "Seleccionar Idioma",
        "language_en": "English",
        "language_es": "Español",
        "save": "GUARDAR",
        "restart_msg": "Reinicia los asistentes para aplicar el idioma."
    },
    "en": {
        "welcome": "Welcome to AstroOrange!",
        "setup_panel": "Configuration Panel",
        "recommended": "Recommended to start:",
        "start_tutorial": "START FULL TUTORIAL",
        "tools": "Individual Tools:",
        "config_user": "Configure User",
        "config_wifi": "Configure WiFi Network",
        "install_soft": "Install Software",
        "no_more_show": "Do not show this panel at login",
        "setup_done_msg": "The wizard will no longer show up automatically.",
        "tutorial_complete": "Configuration complete!",
        "ask_wifi": "Do you want to configure WiFi?",
        "ask_software": "Do you want to install software?",
        "exit": "EXIT",
        "abort": "ABORT INSTALLATION",
        "installed": "INSTALLED",
        "start_install": "START INSTALLATION",
        "processing": "Processing...",
        "installing_pkgs": "Installing selected packages",
        "restart_wizard": "RESTART WIZARD TO SEE CHANGES",
        "critical_error": "CRITICAL ERROR",
        "fatal_error": "Fatal Error",
        "next": "NEXT",
        "back": "BACK",
        "finish": "FINISH",
        "user_manager": "User Manager",
        "create_user": "Create User",
        "username": "Username:",
        "password": "Password:",
        "confirm_password": "Confirm Password:",
        "autologin": "Automatic Login",
        "network_manager": "Network Manager",
        "scanning": "Scanning...",
        "connect": "CONNECT",
        "password_required": "Password Required",
        "manual_connect": "Manual Connection",
        "select_language": "Select Language",
        "language_en": "English",
        "language_es": "Español",
        "save": "SAVE",
        "restart_msg": "Restart the wizards to apply the language."
    }
}

def get_lang():
    if os.path.exists(LANG_FILE):
        try:
            with open(LANG_FILE, "r") as f:
                lang = f.read().strip()
                if lang in TRANSLATIONS:
                    return lang
        except: pass
    return "es"

def t(key):
    lang = get_lang()
    return TRANSLATIONS[lang].get(key, key)
