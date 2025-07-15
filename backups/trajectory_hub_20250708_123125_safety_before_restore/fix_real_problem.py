# === fix_real_problem.py ===
# 🔧 Fix: El problema NO es MacroRotation - es otro componente!
# ⚡ SOLUCIÓN REAL

import os

print("🎯 SOLUCIÓN REAL - El error está en OTRO componente")
print("="*50)

# Basándonos en el test original, el error dice "macro_rotation" pero puede ser engañoso
# Vamos a revisar TODOS los componentes que tienen 'enabled'

print("\n🔍 Revisando TODOS los componentes con 'enabled'...")

with open("trajectory_hub/core/motion_components.py", 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')

# Las líneas problemáticas encontradas
problem_lines = [
    (114, "ConcentrationComponent"),
    (325, "Unknown"),
    (532, "Unknown"),
    (580, "Unknown"),
    (616, "IndividualTrajectory"),
    (657, "Unknown"),
    (717, "MacroRotation"),
    (801, "Unknown"),
    (870, "Unknown"),
    (874, "Unknown")
]

# Identificar a qué clase pertenece cada línea
for line_num, _ in problem_lines:
    if line_num < len(lines):
        # Buscar la clase
        for i in range(line_num-1, -1, -1):
            if 'class ' in lines[i]:
                class_name = lines[i].strip().split('(')[0].replace('class ', '')
                print(f"Línea {line_num}: {class_name} - {lines[line_num-1].strip()}")
                break

print("\n🔧 Aplicando correcciones a TODOS los componentes...")

# Aplicar fixes a todas las comparaciones de enabled
fixes_applied = 0
for i, line in enumerate(lines):
    original = line
    
    # Fix 1: if not self.enabled
    if 'if not self.enabled:' in line and 'or not' not in line:
        indent = len(line) - len(line.lstrip())
        lines[i] = ' ' * indent + 'if not getattr(self, "enabled", False):'
        fixes_applied += 1
        print(f"✅ Fix aplicado línea {i+1}: 'if not self.enabled' → 'if not getattr(...)'")
    
    # Fix 2: if self.enabled
    elif 'if self.enabled:' in line:
        indent = len(line) - len(line.lstrip())
        lines[i] = ' ' * indent + 'if getattr(self, "enabled", False):'
        fixes_applied += 1
        print(f"✅ Fix aplicado línea {i+1}: 'if self.enabled' → 'if getattr(...)'")
    
    # Fix 3: component.enabled
    elif 'if component.enabled:' in line:
        indent = len(line) - len(line.lstrip())
        lines[i] = ' ' * indent + 'if getattr(component, "enabled", False):'
        fixes_applied += 1
        print(f"✅ Fix aplicado línea {i+1}: 'component.enabled' → 'getattr(...)'")
    
    # Fix 4: force['enabled']
    elif "if not force['enabled']:" in line:
        indent = len(line) - len(line.lstrip())
        lines[i] = ' ' * indent + "if not bool(force.get('enabled', False)):"
        fixes_applied += 1
        print(f"✅ Fix aplicado línea {i+1}: force['enabled'] → bool(force.get(...))")

print(f"\n📊 Total de correcciones aplicadas: {fixes_applied}")

# Guardar
with open("trajectory_hub/core/motion_components.py", 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print("✅ motion_components.py actualizado")

# Ahora el error específico del test - create_source necesita source_id=None
print("\n🔧 Creando test corregido...")

test_code = '''
# Test final de rotaciones MS
import sys
sys.path.append('.')

from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np

print("\\n🎯 TEST FINAL: Rotación MS Algorítmica\\n")

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=50, fps=60)
print("✅ Engine creado")

# Crear fuentes con nombres descriptivos
source_ids = []
positions = [
    [2.0, 2.0, 0.0],    # Superior derecha
    [-2.0, 2.0, 0.0],   # Superior izquierda
    [-2.0, -2.0, 0.0],  # Inferior izquierda
    [2.0, -2.0, 0.0]    # Inferior derecha
]

for i, pos in enumerate(positions):
    sid = engine.create_source(f"rotacion_{i}")
    if sid is not None:
        engine._positions[sid] = np.array(pos)
        source_ids.append(sid)
        print(f"✅ Fuente {sid} creada: rotacion_{i}")

# Crear macro
macro_name = engine.create_macro("macro_0_rotacion", source_ids[:4])
print(f"✅ Macro creado: {macro_name}")

# Aplicar rotación
print("\\n🔄 Aplicando rotación...")
engine.set_macro_rotation(macro_name, speed_x=0.0, speed_y=1.0, speed_z=0.0)
print("✅ Rotación configurada")

# Simular
print("\\n⏱️ Simulando 60 frames (1 segundo)...")
for frame in range(60):
    try:
        engine.update()
        if frame % 20 == 0:
            print(f"   {int((frame/60)*100)}% completado...")
    except Exception as e:
        print(f"❌ Error en frame {frame}: {e}")
        break

# Verificar movimiento
print("\\n📍 Verificando movimiento:")
for i, sid in enumerate(source_ids[:4]):
    initial = np.array(positions[i])
    current = engine._positions[sid]
    distance = np.linalg.norm(current - initial)
    angle = np.arctan2(current[2] - 0, current[0] - 0) - np.arctan2(initial[2] - 0, initial[0] - 0)
    angle_deg = np.degrees(angle) % 360
    
    print(f"   Fuente {sid}: movió {distance:.2f} unidades, rotó {angle_deg:.1f}°")

print("\\n✅ TEST COMPLETADO")
'''

with open("test_rotation_final_fixed.py", "w") as f:
    f.write(test_code)

print("\n" + "="*50)
print("🚀 EJECUTANDO TEST CORREGIDO...")
print("="*50)
os.system("python test_rotation_final_fixed.py")