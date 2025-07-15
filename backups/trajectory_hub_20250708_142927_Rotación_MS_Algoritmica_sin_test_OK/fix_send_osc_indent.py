# === fix_send_osc_indent.py ===
# 🔧 Fix: Corregir indentación en _send_osc_update
# ⚡ Impacto: CRÍTICO - Bloquea todo el sistema

import os

file_path = "trajectory_hub/core/enhanced_trajectory_engine.py"

with open(file_path, 'r') as f:
    lines = f.readlines()

# Buscar la línea problemática
for i, line in enumerate(lines):
    if '"""Enviar actualizaciones de posición vía OSC"""' in line and not line.startswith('        '):
        print(f"✅ Encontrada línea mal indentada: {i+1}")
        lines[i] = '        """Enviar actualizaciones de posición vía OSC"""\n'
        break

# Guardar
with open(file_path, 'w') as f:
    f.writelines(lines)

print("✅ Indentación corregida")

# Test rápido
print("\n🚀 Probando import...")
try:
    from trajectory_hub import EnhancedTrajectoryEngine
    print("✅ Import exitoso!")
    
    # Ejecutar debug
    import subprocess
    print("\n🔍 Ejecutando debug...")
    subprocess.run(['python', 'debug_engine_update.py'])
    
except Exception as e:
    print(f"❌ Error: {e}")