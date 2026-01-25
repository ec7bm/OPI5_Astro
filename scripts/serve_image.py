
import http.server
import socketserver
import os
import socket
import sys

# Configuración
PORT = 8000
DIRECTORY = "output"

# Asegurar que estamos en el directorio raíz del proyecto
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, DIRECTORY)

# Cambiar al directorio de salida para servir solo los archivos generados
if os.path.exists(OUTPUT_DIR):
    os.chdir(OUTPUT_DIR)
else:
    print(f"Error: No se encuentra el directorio {OUTPUT_DIR}")
    print("Asegúrate de ejecutar este script después de que termine la compilación.")
    sys.exit(1)

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.getcwd(), **kwargs)

try:
    # Intentar detectar la IP local de la VM
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    
    print(f"\n==================================================")
    print(f"✅  SERVIDOR DE DESCARGA ACTIVO")
    print(f"==================================================")
    print(f"📂 Sirviendo archivos de: {os.getcwd()}")
    print(f"🔗 URL para descargar en Windows: http://{ip}:{PORT}")
    print(f"==================================================")
    print(f"(Presiona Ctrl+C para detener el servidor cuando termines)")
    
    # Permitir reutilizar el puerto inmediatamente
    socketserver.TCPServer.allow_reuse_address = True
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        httpd.serve_forever()

except KeyboardInterrupt:
    print("\n🛑 Servidor detenido.")
except Exception as e:
    print(f"\n❌ Error al iniciar el servidor: {e}")
