# === fix_update_with_deltas.py ===
# 🔧 Fix: Verificar y corregir la definición de update_with_deltas
# ⚡ El error sugiere un problema con self

import os
import re

print("🔍 Buscando y corrigiendo update_with_deltas...")

file_path = "trajectory_hub/core/motion_components.py"

with open(file_path, 'r') as f:
    content = f.read()

# Buscar la definición de update_with_deltas
pattern = r'def update_with_deltas\([^)]*\):'
matches = list(re.finditer(pattern, content))

print(f"\n📋 Encontradas {len(matches)} definiciones de update_with_deltas:")
for match in matches:
    line_start = content.rfind('\n', 0, match.start()) + 1
    line_end = content.find('\n', match.end())
    line = content[line_start:line_end]
    print(f"  '{line.strip()}'")

# El problema es que probablemente falta self
# Buscar específicamente en SourceMotion
source_motion_pos = content.find("class SourceMotion:")
if source_motion_pos != -1:
    # Buscar update_with_deltas después de SourceMotion
    update_pos = content.find("def update_with_deltas", source_motion_pos)
    if update_pos != -1:
        # Verificar si tiene self
        line_end = content.find(":", update_pos)
        method_def = content[update_pos:line_end+1]
        print(f"\n🔍 Definición actual en SourceMotion: '{method_def}'")
        
        if "self" not in method_def:
            print("❌ Falta 'self' en la definición!")
            # Corregir
            content = content[:update_pos] + "    def update_with_deltas(self, dt: float)" + content[line_end:]
            
            with open(file_path, 'w') as f:
                f.write(content)
            print("✅ Corregido!")

# Test rápido
test_code = '''# === test_individual_quick.py ===
from trajectory_hub import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import IndividualTrajectory, TrajectoryMovementMode
import numpy as np

print("🧪 Test rápido de IndividualTrajectory...")

# Setup mínimo
engine = EnhancedTrajectoryEngine(max_sources=1, fps=60)
engine.create_macro("test", [0])

motion = engine.motion_states[0]
traj = IndividualTrajectory()
traj.enabled = True
traj.shape_type = "circle"
traj.shape_params = {"radius": 2.0}
traj.movement_mode = TrajectoryMovementMode.FIX
traj.movement_speed = 1.0
traj.center = np.zeros(3)
motion.active_components['individual_trajectory'] = traj

print("✅ Configurado")

# Test update_with_deltas
print("\\n🧪 Probando update_with_deltas...")
try:
    deltas = motion.update_with_deltas(0.1)
    print(f"✅ Funcionó! Deltas: {len(deltas)}")
    if deltas:
        print(f"   Delta[0]: {deltas[0].position}")
except Exception as e:
    print(f"❌ Error: {e}")

# Simulación rápida
print("\\n🏃 Simulación rápida (1 segundo)...")
initial = engine._positions[0].copy()

for i in range(60):
    dt = 1/60
    try:
        deltas = motion.update_with_deltas(dt)
        for delta in deltas:
            if delta and delta.position is not None:
                engine._positions[0] += delta.position
    except Exception as e:
        print(f"❌ Error en frame {i}: {e}")
        break

final = engine._positions[0]
distance = np.linalg.norm(final - initial)

print(f"\\n📊 Resultado:")
print(f"   Posición inicial: {initial}")
print(f"   Posición final: {final}")
print(f"   Distancia: {distance:.3f}")
print(f"   Phase final: {traj.position_on_trajectory:.3f}")

if distance > 0.1:
    print("\\n✅ ¡IndividualTrajectory funciona con deltas!")
    print("\\n📝 Próximos pasos:")
    print("   1. Arreglar engine.update() para procesar deltas automáticamente")
    print("   2. Migrar MacroTrajectory a deltas")
    print("   3. Migrar rotaciones a deltas")
else:
    print("\\n❌ No hubo movimiento suficiente")
'''

with open("test_individual_quick.py", "w") as f:
    f.write(test_code)

print("\n✅ Test creado: test_individual_quick.py")
print("🚀 Ejecutando...")

import subprocess
result = subprocess.run(['python', 'test_individual_quick.py'], 
                      capture_output=True, text=True)
print(result.stdout)
if result.stderr and "No se puede crear modulador" not in result.stderr:
    print("Errores:", result.stderr)