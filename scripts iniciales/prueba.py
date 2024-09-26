import sys
import platform

# Obtener la versión de Python
python_version = platform.python_version()

# Obtener la ruta de instalación de Python
python_path = sys.executable

print(f"Versión de Python: {python_version}")
print(f"Ruta de instalación de Python: {python_path}")