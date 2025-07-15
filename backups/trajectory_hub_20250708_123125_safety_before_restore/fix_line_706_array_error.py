# === fix_line_706_array_error.py ===
# 🔧 Fix: Error array ambiguous en línea 706
# ⚡ Líneas modificadas: 702-706
# 🎯 Impacto: ALTO

import re
import shutil
from datetime import datetime
import numpy as np

def fix_array_error():
    """Arregla el error de comparación con arrays en línea 706"""
    
    # Verificar estructura de directorios
    import os
    if os.path.exists("core/motion_components.py"):
        file_path = "core/motion_components.py"
    elif os.path.exists("motion_components.py"):
        file_path = "motion_components.py"
    else:
        print("❌ No se encuentra motion_components.py")
        print("   Archivos disponibles:")
        for f in os.listdir("."):
            if f.endswith(".py"):
                print(f"   - {f}")
        if os.path.exists("core"):
            print("   En core/:")
            for f in os.listdir("core"):
                if f.endswith(".py"):
                    print(f"   - core/{f}")
        return
    
    print(f"📁 Usando archivo: {file_path}")
    
    # Backup
    backup_name = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy(file_path, backup_name)
    print(f"✅ Backup creado: {backup_name}")
    
    # Leer archivo
    with open(file_path, "r") as f:
        lines = f.readlines()
    
    # Buscar y arreglar la línea problemática
    fixed = False
    for i in range(len(lines)):
        # Buscar el método set_rotation_speeds
        if i > 0 and "def set_rotation_speeds" in lines[i-1]:
            # Buscar las líneas 702-706
            for j in range(i, min(i + 20, len(lines))):
                if "self.enabled = bool(abs(speed_x)" in lines[j]:
                    print(f"\n🔍 Encontrado error en línea {j+1}:")
                    print(f"   Antes: {lines[j].strip()}")
                    
                    # Reemplazar toda la sección del método
                    indent = "        "
                    lines[j-4] = f"{indent}self.speed_x = float(speed_x) if np.isscalar(speed_x) else float(speed_x[0] if len(speed_x) > 0 else 0.0)\n"
                    lines[j-3] = f"{indent}self.speed_y = float(speed_y) if np.isscalar(speed_y) else float(speed_y[0] if len(speed_y) > 0 else 0.0)\n"
                    lines[j-2] = f"{indent}self.speed_z = float(speed_z) if np.isscalar(speed_z) else float(speed_z[0] if len(speed_z) > 0 else 0.0)\n"
                    lines[j-1] = f"{indent}# Usar comparación segura para evitar problemas con arrays\n"
                    lines[j] = f"{indent}self.enabled = (abs(self.speed_x) > 0.001) or (abs(self.speed_y) > 0.001) or (abs(self.speed_z) > 0.001)\n"
                    
                    print(f"   Después: {lines[j].strip()}")
                    fixed = True
                    break
        if fixed:
            break
    
    if fixed:
        # Escribir archivo corregido
        with open(file_path, "w") as f:
            f.writelines(lines)
        print("\n✅ Archivo corregido exitosamente")
        
        # Verificar con test rápido
        print("\n🧪 Verificando fix con test rápido...")
        test_conversion()
    else:
        print("❌ No se encontró la línea problemática")

def test_conversion():
    """Test para verificar que la conversión funciona"""
    print("\n📋 Test de conversión:")
    
    # Casos de prueba
    test_cases = [
        (1.0, "float normal"),
        (np.array([1.0]), "array 1D con 1 elemento"),
        (np.array([1.0, 2.0]), "array 1D con múltiples elementos"),
        (np.array([[1.0]]), "array 2D"),
        (0.0, "cero"),
        (np.array([]), "array vacío")
    ]
    
    for value, desc in test_cases:
        try:
            # Simular la conversión
            if np.isscalar(value):
                result = float(value)
            else:
                result = float(value[0] if len(value) > 0 else 0.0)
            
            # Simular la comparación
            enabled = (abs(result) > 0.001)
            
            print(f"   {desc}: {value} → {result} → enabled={enabled} ✅")
        except Exception as e:
            print(f"   {desc}: {value} → ERROR: {e} ❌")

if __name__ == "__main__":
    print("🔧 Arreglando error de array ambiguous en línea 706")
    print("=" * 50)
    fix_array_error()
    
    print("\n📝 Próximo paso:")
    print("   python test_rotation_ms_final.py")