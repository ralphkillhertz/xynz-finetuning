# 🔧 Fix: Añadir funciones faltantes a interface_utils.py
# ⚡ Líneas añadidas: Todas las funciones necesarias

print("🔧 Arreglando interface_utils.py...")

interface_utils_content = '''"""
Utilidades para la interfaz interactiva
"""
import os
from typing import Optional, Union


def validate_numeric_input(value: str, min_val: float = None, max_val: float = None) -> Optional[float]:
    """Valida entrada numérica del usuario"""
    try:
        num = float(value)
        if min_val is not None and num < min_val:
            return None
        if max_val is not None and num > max_val:
            return None
        return num
    except ValueError:
        return None


def format_time(seconds: float) -> str:
    """Formatea tiempo en formato legible"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        mins = seconds // 60
        secs = seconds % 60
        return f"{int(mins)}m {int(secs)}s"
    else:
        hours = seconds // 3600
        mins = (seconds % 3600) // 60
        return f"{int(hours)}h {int(mins)}m"


def print_separator(char: str = "=", width: int = 60):
    """Imprime separador visual"""
    print(char * width)


def get_user_confirmation(prompt: str = "¿Continuar? (s/n): ") -> bool:
    """Obtiene confirmación del usuario"""
    while True:
        response = input(prompt).lower().strip()
        if response in ['s', 'si', 'yes', 'y']:
            return True
        elif response in ['n', 'no']:
            return False
        print("Por favor responda 's' o 'n'")


# Funciones originales si las hay
def clear_screen():
    """Limpia la pantalla de la consola"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(title: str):
    """Imprime un encabezado formateado"""
    print_separator()
    print(f" {title} ".center(60))
    print_separator()
'''

# Guardar
with open("trajectory_hub/interface/interface_utils.py", 'w', encoding='utf-8') as f:
    f.write(interface_utils_content)

print("✅ interface_utils.py actualizado")
print("\n🚀 Ahora prueba de nuevo:")
print("   python -m trajectory_hub.interface.interactive_controller")