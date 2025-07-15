# === fix_line_706_direct.py ===
# 🔧 Fix: Error array ambiguous línea 706 en MacroRotation
# ⚡ Solución directa al problema
# 🎯 Impacto: CRÍTICO

import re
import shutil
from datetime import datetime

def fix_array_error():
    """Arregla directamente el error en línea 706"""
    
    file_path = "trajectory_hub/core/motion_components.py"
    
    # Backup
    backup_name = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy(file_path, backup_name)
    print(f"✅ Backup creado: {backup_name}")
    
    # Leer archivo
    with open(file_path, "r") as f:
        content = f.read()
    
    # Buscar y reemplazar la línea problemática
    # Patrón original (línea 706)
    pattern = r'self\.enabled = bool\(abs\(speed_x\) > 0\.001 or abs\(speed_y\) > 0\.001 or abs\(speed_z\) > 0\.001\)'
    
    # Reemplazo seguro
    replacement = '''# Convertir a float si es array
        sx = float(speed_x) if hasattr(speed_x, '__len__') else float(speed_x)
        sy = float(speed_y) if hasattr(speed_y, '__len__') else float(speed_y)
        sz = float(speed_z) if hasattr(speed_z, '__len__') else float(speed_z)
        self.enabled = (abs(sx) > 0.001) or (abs(sy) > 0.001) or (abs(sz) > 0.001)'''
    
    # Contar ocurrencias
    count = len(re.findall(pattern, content))
    print(f"\n🔍 Encontradas {count} ocurrencias del patrón")
    
    if count > 0:
        # Reemplazar
        new_content = re.sub(pattern, replacement, content)
        
        # Escribir archivo
        with open(file_path, "w") as f:
            f.write(new_content)
        
        print("✅ Archivo corregido exitosamente")
        
        # Buscar otras comparaciones problemáticas
        print("\n🔍 Buscando otras comparaciones que podrían fallar...")
        check_other_issues(file_path)
    else:
        print("❌ No se encontró el patrón exacto")
        print("\n📋 Buscando líneas similares...")
        
        # Buscar líneas que contengan 'enabled' y 'or'
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'self.enabled' in line and ' or ' in line and 'abs(' in line:
                print(f"   Línea {i+1}: {line.strip()}")

def check_other_issues(file_path):
    """Busca otras comparaciones problemáticas"""
    with open(file_path, "r") as f:
        lines = f.readlines()
    
    problematic = []
    for i, line in enumerate(lines):
        # Buscar comparaciones con 'or' que podrían tener arrays
        if ' or ' in line and any(op in line for op in ['>', '<', '>=', '<=', '==']):
            # Excluir strings y comentarios
            if not (line.strip().startswith('#') or line.strip().startswith('"') or line.strip().startswith("'")):
                problematic.append((i+1, line.strip()))
    
    if problematic:
        print(f"\n⚠️ Encontradas {len(problematic)} líneas con comparaciones 'or' potencialmente problemáticas:")
        for line_no, line in problematic[:5]:  # Mostrar solo las primeras 5
            print(f"   Línea {line_no}: {line}")

if __name__ == "__main__":
    print("🔧 Arreglando error array ambiguous - Solución Directa")
    print("=" * 50)
    fix_array_error()
    
    print("\n📝 Próximo paso:")
    print("   python test_rotation_ms_final.py")