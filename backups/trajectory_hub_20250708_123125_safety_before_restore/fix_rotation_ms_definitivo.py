# === fix_rotation_ms_definitivo.py ===
# 🔧 Fix: SOLUCIÓN DEFINITIVA para error de arrays
# ⚡ 10 MINUTOS PARA LA GLORIA

import os
import re

print("🚀 FIX DEFINITIVO - ROTACIONES MS")
print("="*50)

# Paso 1: Localizar el error exacto
print("\n🔍 Localizando error en MacroRotation...")

with open("trajectory_hub/core/motion_components.py", 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Buscar la línea problemática en calculate_delta
found_error = False
for i, line in enumerate(lines):
    if 'class MacroRotation' in line:
        print(f"✓ MacroRotation encontrada en línea {i+1}")
        # Buscar dentro de calculate_delta
        for j in range(i, min(i+100, len(lines))):
            if 'if not self.enabled:' in lines[j]:
                print(f"✓ Encontrado check de enabled en línea {j+1}")
                # El problema es que self.enabled es un array, no un bool
                lines[j] = lines[j].replace('if not self.enabled:', 'if not self.enabled or not any([self.speed_x, self.speed_y, self.speed_z]):')
                found_error = True
                print("✅ Error corregido - check de enabled")
                break

# Buscar más problemas de comparación de arrays
fixes_applied = 0
for i, line in enumerate(lines):
    # Corregir comparaciones con speed que pueden ser arrays
    if 'if abs(self.speed_' in line and ') > 0.001:' in line:
        # Extraer la variable
        var_match = re.search(r'if abs\(self\.(speed_[xyz])\) > 0\.001:', line)
        if var_match:
            var_name = var_match.group(1)
            new_line = line.replace(
                f'if abs(self.{var_name}) > 0.001:',
                f'if abs(float(self.{var_name})) > 0.001:'
            )
            lines[i] = new_line
            fixes_applied += 1
            print(f"✅ Corregido check de {var_name} en línea {i+1}")

print(f"\n📊 Total de correcciones aplicadas: {fixes_applied + (1 if found_error else 0)}")

# Paso 2: Asegurar que enabled se inicializa como bool
for i, line in enumerate(lines):
    if 'self.enabled = any([speed_x, speed_y, speed_z])' in line:
        lines[i] = '        self.enabled = bool(any([speed_x, speed_y, speed_z]))\n'
        print("✅ Corregido inicialización de enabled como bool")
        break

# Paso 3: Guardar cambios
with open("trajectory_hub/core/motion_components.py", 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("\n✅ motion_components.py actualizado")

# Paso 4: Verificar sintaxis
print("\n🧪 Verificando sintaxis...")
import py_compile
try:
    py_compile.compile("trajectory_hub/core/motion_components.py", doraise=True)
    print("✅ Sintaxis correcta")
except Exception as e:
    print(f"❌ Error de sintaxis: {e}")
    exit(1)

# Paso 5: Test rápido para verificar el fix
print("\n🧪 Test rápido del fix...")
test_code = '''
import numpy as np
import sys
sys.path.append('.')

from trajectory_hub.core.motion_components import MacroRotation, MotionState, MotionDelta

# Test 1: Crear MacroRotation
rotation = MacroRotation()
print("✅ MacroRotation creada")

# Test 2: Set rotation
rotation.set_rotation(0.0, 1.0, 0.0)
print(f"✅ Rotación configurada - enabled: {rotation.enabled}")

# Test 3: Calculate delta
state = MotionState()
state.position = np.array([2.0, 2.0, 0.0])
rotation.update_center(np.array([0.0, 0.0, 0.0]))

delta = rotation.calculate_delta(state, 0.0, 0.1)
print(f"✅ Delta calculado: {delta.position}")
print(f"   Posición debería cambiar: {np.linalg.norm(delta.position) > 0.01}")
'''

with open("test_fix_quick.py", "w") as f:
    f.write(test_code)

os.system("python test_fix_quick.py")
os.remove("test_fix_quick.py")

print("\n" + "="*50)
print("🎯 EJECUTANDO TEST FINAL...")
print("="*50)
os.system("python test_rotation_ms_final.py")