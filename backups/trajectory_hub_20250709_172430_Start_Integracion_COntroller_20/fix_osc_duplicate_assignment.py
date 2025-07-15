import re

def fix_osc_duplicate():
    file_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    # Leer archivo
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    # Buscar y eliminar la línea problemática
    fixed_lines = []
    removed = False
    
    for i, line in enumerate(lines):
        # Skip la línea que pone osc_bridge = None
        if "self.osc_bridge = None" in line and i > 50:  # Asegurar que es la segunda
            print(f"❌ Eliminando línea {i+1}: {line.strip()}")
            removed = True
            continue
        fixed_lines.append(line)
    
    if removed:
        # Backup
        import shutil
        from datetime import datetime
        backup = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy(file_path, backup)
        print(f"✅ Backup: {backup}")
        
        # Escribir corregido
        with open(file_path, 'w') as f:
            f.writelines(fixed_lines)
        
        print("✅ Asignación duplicada eliminada")
        print("🚀 Ejecuta: python test_osc_debug.py")
    else:
        print("⚠️ No se encontró la línea problemática")

if __name__ == "__main__":
    fix_osc_duplicate()