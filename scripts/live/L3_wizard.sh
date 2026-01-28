#!/bin/bash
# L3_wizard.sh - El Asistente de Configuración

set -e
echo "🧙 Configurando el Wizard..."

# Asegurar carpetas
sudo mkdir -p /opt/astroorange/wizard
# Copiar el main.py que ya tenemos en el repo
sudo cp ../../wizard/main.py /opt/astroorange/wizard/
sudo chmod +x /opt/astroorange/wizard/main.py

# Configurar Autostart
mkdir -p ~/.config/autostart
cat <<EOF > ~/.config/autostart/astro-wizard.desktop
[Desktop Entry]
Type=Application
Name=AstroWizard
Exec=python3 /opt/astroorange/wizard/main.py
OnlyShowIn=XFCE;
EOF

echo "✅ Wizard configurado. Aparecerá la próxima vez que inicies sesión en el escritorio."
