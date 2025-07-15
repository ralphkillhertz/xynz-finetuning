# === fix_line_1905.py ===
# 🔧 Fix: La línea 1905 tiene 1 espacio cuando debería estar vacía
# ⚡ Esto causa el error de indentación

import os
import shutil
from datetime import datetime

print("🔧 Arreglando línea 1905 con espacio incorrecto...")

file_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(file_path, backup_path)

with open(file_path, 'r') as f:
    lines = f.readlines()

# Arreglar línea 1905 (índice 1904)
if len(lines) > 1904:
    print(f"Línea 1905 actual: '{lines[1904]}'")
    print(f"  Longitud: {len(lines[1904])}")
    print(f"  Repr: {repr(lines[1904])}")
    
    # Cambiar a línea vacía
    lines[1904] = '\n'
    print("✅ Línea 1905 corregida (ahora es línea vacía)")

# Guardar
with open(file_path, 'w') as f:
    f.writelines(lines)

print(f"✅ Backup: {backup_path}")

# Verificar
print("\n🧪 Verificando...")
try:
    import sys
    # Limpiar cache
    for module in list(sys.modules.keys()):
        if module.startswith('trajectory_hub'):
            del sys.modules[module]
    
    from trajectory_hub import EnhancedTrajectoryEngine
    print("✅ Import exitoso!")
    
    # Ejecutar test
    print("\n🚀 Ejecutando test de engine.update()...")
    import subprocess
    result = subprocess.run(['python', 'test_engine_auto_deltas.py'], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print("\n✅ TEST EXITOSO!")
        # Mostrar solo líneas importantes
        for line in result.stdout.split('\n'):
            if any(word in line for word in ['Test', 'configurado', 'Frame', '✅', '❌', 'ÉXITO', 'RESULTADOS', 'automáticamente']):
                print(line)
    else:
        print(f"\n❌ Error en test: {result.stderr}")
        
except Exception as e:
    print(f"❌ Error: {e}")