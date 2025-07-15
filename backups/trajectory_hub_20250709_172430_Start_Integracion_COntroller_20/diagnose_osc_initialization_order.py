# 🔍 Diagnóstico completo del problema de inicialización
# 🎯 Causa raíz: Logger intenta acceder a osc_bridge ANTES de crearlo

import re
from datetime import datetime

print("🔍 ANÁLISIS PROFUNDO - Orden de inicialización OSC")
print("=" * 60)

# 1. Analizar el __init__ completo
engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
with open(engine_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 2. Encontrar el método __init__ completo
init_match = re.search(r'def __init__\(self.*?\n(?=\n    def|\nclass|\Z)', content, re.DOTALL)
if init_match:
    init_method = init_match.group(0)
    
    print("📋 Estructura actual del __init__:")
    # Mostrar líneas relevantes
    lines = init_method.split('\n')
    for i, line in enumerate(lines):
        if 'osc' in line.lower() or 'bridge' in line.lower():
            print(f"  Línea {i}: {line}")

# 3. Identificar el problema
print("\n❌ PROBLEMA IDENTIFICADO:")
print("  - logger.info() intenta acceder a self.osc_bridge")
print("  - PERO self.osc_bridge se crea DESPUÉS")
print("  - Orden incorrecto de las líneas")

# 4. Solución integral
fix_code = '''# === fix_osc_initialization_order.py ===
# 🔧 Fix: Corregir orden de inicialización de OSC
# ⚡ Mover logger DESPUÉS de crear osc_bridge

import shutil
from datetime import datetime

print("🔧 Corrigiendo orden de inicialización OSC...")

# Backup
engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
backup_file = f"{engine_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(engine_file, backup_file)
print(f"✅ Backup: {backup_file}")

# Leer archivo
with open(engine_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Buscar las líneas problemáticas
osc_lines = []
indices_to_remove = []

for i, line in enumerate(lines):
    if 'logger.info("Inicializando OSC bridge' in line:
        indices_to_remove.append(i)
    elif 'logger.info(f"OSC bridge inicializado:' in line:
        indices_to_remove.append(i)
    elif 'self.osc_bridge = SpatOSCBridge()' in line:
        osc_init_index = i

# Reordenar: primero crear, luego loggear
new_lines = []
for i, line in enumerate(lines):
    if i not in indices_to_remove:
        new_lines.append(line)
        # Si acabamos de crear osc_bridge, añadir los logs
        if i == osc_init_index:
            new_lines.append('        logger.info(f"OSC bridge inicializado: {self.osc_bridge is not None}")\\n')

# Guardar
with open(engine_file, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✅ Orden corregido:")
print("  1. self.osc_bridge = SpatOSCBridge()")
print("  2. logger.info(...)")
print("\\n🚀 Ejecuta: python test_osc_debug.py")
'''

# Guardar script de corrección
with open("fix_osc_initialization_order.py", 'w') as f:
    f.write(fix_code)

print("\n✅ Script de corrección creado")
print("\n🚀 Ejecuta: python fix_osc_initialization_order.py")