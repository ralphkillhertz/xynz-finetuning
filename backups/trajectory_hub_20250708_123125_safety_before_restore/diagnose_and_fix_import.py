# === diagnose_and_fix_import.py ===
# 🔧 Diagnóstico: Por qué no se ve set_macro_rotation
# ⚡ Impacto: CRÍTICO - Resuelve problema de import

import os
import sys

def diagnose_and_fix():
    """Diagnostica y arregla el problema de import"""
    
    print("🔍 DIAGNÓSTICO DEL PROBLEMA DE IMPORT\n")
    
    # 1. Verificar que el método existe en el archivo
    print("1️⃣ Verificando archivo fuente...")
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    with open(engine_path, 'r') as f:
        content = f.read()
    
    if 'def set_macro_rotation' in content:
        print("✅ set_macro_rotation EXISTE en el archivo")
        
        # Verificar indentación
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'def set_macro_rotation' in line:
                indent = len(line) - len(line.lstrip())
                print(f"   Línea {i+1}: indentación = {indent} espacios")
                if indent != 4:
                    print("   ❌ PROBLEMA: Debe tener 4 espacios")
                else:
                    print("   ✅ Indentación correcta")
                    
                # Ver líneas alrededor
                print("\n   Contexto:")
                for j in range(max(0, i-2), min(len(lines), i+3)):
                    print(f"   L{j+1}: {lines[j][:60]}")
    else:
        print("❌ set_macro_rotation NO EXISTE")
    
    # 2. Test directo de import con recarga
    print("\n2️⃣ Test de import con recarga forzada...")
    
    test_reload = '''# === test_with_reload.py ===
# Test con recarga forzada del módulo

import importlib
import sys

# Eliminar módulos del cache
modules_to_remove = []
for module_name in sys.modules:
    if 'trajectory_hub' in module_name:
        modules_to_remove.append(module_name)

for module_name in modules_to_remove:
    del sys.modules[module_name]

print("✅ Cache limpiado")

# Importar fresh
from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np

print("✅ Import fresh completado")

# Verificar métodos
print("\\n🔍 Métodos que contienen 'rotation':")
for attr in dir(EnhancedTrajectoryEngine):
    if 'rotation' in attr.lower():
        print(f"   - {attr}")

# Verificar específicamente
if hasattr(EnhancedTrajectoryEngine, 'set_macro_rotation'):
    print("\\n✅ set_macro_rotation EXISTE")
else:
    print("\\n❌ set_macro_rotation NO EXISTE")
    
    # Listar todos los métodos set_
    print("\\n📋 Métodos set_* disponibles:")
    for attr in dir(EnhancedTrajectoryEngine):
        if attr.startswith('set_'):
            print(f"   - {attr}")

# Intentar crear instancia y usar
try:
    engine = EnhancedTrajectoryEngine(max_sources=4, fps=60, enable_modulator=False)
    print("\\n✅ Engine creado")
    
    # Crear macro
    macro_id = engine.create_macro("test", 2)
    print(f"✅ Macro creado: {macro_id}")
    
    # Intentar rotación
    if hasattr(engine, 'set_macro_rotation'):
        engine.set_macro_rotation(macro_id, 0, 1.0, 0)
        print("✅ Rotación aplicada!")
    else:
        print("❌ El método no existe en la instancia")
        
        # Debug: ver qué tiene la instancia
        print("\\n🔍 Métodos de la instancia con 'macro':")
        for attr in dir(engine):
            if 'macro' in attr.lower() and not attr.startswith('_'):
                print(f"   - {attr}")
                
except Exception as e:
    print(f"\\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
'''
    
    with open("test_with_reload.py", "w") as f:
        f.write(test_reload)
    
    print("\n✅ Test de recarga creado")
    
    # 3. Fix directo si es problema de indentación
    print("\n3️⃣ Aplicando fix de indentación...")
    
    # Leer líneas
    with open(engine_path, 'r') as f:
        lines = f.readlines()
    
    # Buscar y corregir
    for i, line in enumerate(lines):
        if 'def set_macro_rotation' in line and not line.startswith('    def'):
            print(f"❌ Línea {i+1} tiene indentación incorrecta")
            lines[i] = '    ' + line.lstrip()
            print("✅ Corregida")
    
    # Guardar
    with open(engine_path, 'w') as f:
        f.writelines(lines)
    
    print("\n✅ Archivo actualizado")

if __name__ == "__main__":
    diagnose_and_fix()
    print("\n🚀 Ejecutando test con recarga...")
    os.system("python test_with_reload.py")