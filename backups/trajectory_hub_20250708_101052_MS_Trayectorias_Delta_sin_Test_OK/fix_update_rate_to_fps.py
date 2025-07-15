# === fix_update_rate_to_fps.py ===
# 🔧 Fix: El engine usa fps, no _update_rate
# ⚡ Cambiar todas las referencias

import os
import shutil
from datetime import datetime

print("🔧 Cambiando _update_rate por fps...")

file_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(file_path, backup_path)

with open(file_path, 'r') as f:
    content = f.read()

# Cambiar todas las referencias de _update_rate a fps
changes = 0
original = content
content = content.replace('self._update_rate', 'self.fps')
changes = original.count('self._update_rate')

print(f"✅ Cambiadas {changes} referencias de _update_rate a fps")

# Guardar
with open(file_path, 'w') as f:
    f.write(content)

print(f"✅ Backup: {backup_path}")

# Test completo
print("\n🚀 Ejecutando test...")
import subprocess
result = subprocess.run(['python', 'test_engine_auto_deltas.py'], 
                      capture_output=True, text=True)

if result.returncode == 0:
    print("\n🎉 ¡TEST EXITOSO!")
    # Mostrar resultados importantes
    for line in result.stdout.split('\n'):
        if any(word in line for word in ['Test', 'configurado', 'Frame', '✅', '❌', 'ÉXITO', 'RESULTADOS', 'automáticamente']):
            print(line)
            
    # Guardar estado de éxito
    state_code = '''
import json
state = {
    "individual_trajectory": "✅ Migrado a deltas",
    "engine_update": "✅ Procesa deltas automáticamente", 
    "macro_trajectory": "❌ Pendiente migración",
    "rotation_ms": "❌ Pendiente",
    "rotation_is": "❌ Pendiente",
    "mcp_server": "❌ CRÍTICO - 0%"
}
with open("migration_state.json", "w") as f:
    json.dump(state, f, indent=2)
print("\\n💾 Estado actualizado en migration_state.json")
'''
    exec(state_code)
else:
    print(f"\n❌ Error: {result.stderr}")