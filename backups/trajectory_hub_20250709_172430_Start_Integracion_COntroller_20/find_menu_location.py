import os
import re

def find_menu_exact():
    """Buscar el menú exacto que muestra circle, line, grid, spiral, random"""
    print("🔍 BÚSQUEDA EXACTA DEL MENÚ DE FORMACIONES")
    print("="*60)
    
    # Archivos donde podría estar
    files = [
        "trajectory_hub/interface/interactive_controller.py",
        "trajectory_hub/control/processors/command_processor.py",
        "trajectory_hub/control/interfaces/cli_interface.py"
    ]
    
    for filepath in files:
        if os.path.exists(filepath):
            print(f"\n📂 Buscando en: {filepath}")
            
            with open(filepath, 'r') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Buscar líneas con números seguidos de formaciones
            for i, line in enumerate(lines):
                # Patrón: número seguido de punto y una formación
                if re.search(r'[1-5]\.\s*(circle|line|grid|spiral|random)', line):
                    print(f"\n✅ ENCONTRADO en línea {i+1}:")
                    
                    # Mostrar contexto (10 líneas antes y después)
                    start = max(0, i-10)
                    end = min(len(lines), i+15)
                    
                    for j in range(start, end):
                        marker = ">>>" if j == i else "   "
                        print(f"{marker} {j+1}: {lines[j]}")
                    
                    # Buscar el método que contiene esto
                    # Retroceder para encontrar 'def'
                    for k in range(i, max(0, i-50), -1):
                        if lines[k].strip().startswith('def '):
                            print(f"\n📍 Método: {lines[k].strip()}")
                            break
                    
                    print(f"\n💡 Para añadir sphere aquí:")
                    print(f"   - Archivo: {filepath}")
                    print(f"   - Después de línea {i+1}")
                    print(f"   - Añadir: '  6. sphere'")
                    
                    return filepath, i+1

if __name__ == "__main__":
    result = find_menu_exact()
    if result:
        print(f"\n✅ Menú encontrado en: {result[0]}, línea {result[1]}")
    else:
        print("\n❌ No encontré el menú")