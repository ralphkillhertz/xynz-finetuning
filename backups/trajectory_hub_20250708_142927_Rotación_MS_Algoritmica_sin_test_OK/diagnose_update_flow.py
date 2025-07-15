# === diagnose_update_flow.py ===
# 🔧 Fix: Rastrear el flujo de update completo
# ⚡ Encontrar dónde se rompe la cadena

from trajectory_hub import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import IndividualTrajectory
import numpy as np

print("🔍 Diagnóstico del flujo de update...\n")

# Crear setup básico
engine = EnhancedTrajectoryEngine(max_sources=2, fps=60)
engine.create_macro("test", [0])

# Configurar trayectoria manualmente
motion = engine.motion_states[0]
traj = IndividualTrajectory()
traj.enabled = True
traj.shape_type = "circle"
traj.movement_mode = "fix"
traj.movement_speed = 1.0
traj.set_trajectory("circle", radius=2.0)
motion.active_components['individual_trajectory'] = traj

print("✅ Trayectoria configurada")
print(f"  Phase inicial: {traj.position_on_trajectory}")

# Test 1: update_position funciona?
print("\n🧪 Test 1: traj.update_position()")
if hasattr(traj, 'update_position'):
    traj.update_position(0.1)
    print(f"  Phase después: {traj.position_on_trajectory}")
else:
    print("  ❌ No tiene update_position")

# Test 2: calculate_delta funciona?
print("\n🧪 Test 2: traj.calculate_delta()")
if hasattr(traj, 'calculate_delta'):
    delta = traj.calculate_delta(motion.state, 0.1)
    print(f"  Delta: {delta.position}")
    print(f"  Phase: {traj.position_on_trajectory}")
else:
    print("  ❌ No tiene calculate_delta")

# Test 3: update_with_deltas funciona?
print("\n🧪 Test 3: motion.update_with_deltas()")
deltas = motion.update_with_deltas(0.1)
print(f"  Deltas retornados: {len(deltas)}")
for i, d in enumerate(deltas):
    print(f"    Delta {i}: {d.position}")

# Test 4: engine.update() llama a los updates?
print("\n🧪 Test 4: Rastrear engine.update()")

# Añadir debug hooks
original_update_deltas = motion.update_with_deltas
call_count = [0]

def debug_update_deltas(dt):
    call_count[0] += 1
    print(f"  🔸 update_with_deltas llamado! (#{call_count[0]}, dt={dt})")
    return original_update_deltas(dt)

motion.update_with_deltas = debug_update_deltas

# Llamar engine.update
print("  Llamando engine.update()...")
engine.update()

if call_count[0] == 0:
    print("  ❌ engine.update() NO llama a motion.update_with_deltas()")
else:
    print(f"  ✅ Llamado {call_count[0]} veces")

# Test 5: Ver el código de engine.update
print("\n📄 Examinando engine.update()...")

# Crear fix para engine
fix_code = '''# === fix_engine_update_individual.py ===
import os
import shutil
from datetime import datetime

print("🔧 Arreglando engine.update() para procesar trayectorias individuales...")

file_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(file_path, backup_path)

with open(file_path, 'r') as f:
    content = f.read()

# Buscar el método update
update_pos = content.find("def update(self)")
if update_pos == -1:
    print("❌ No se encontró def update(self)")
else:
    # Buscar dónde procesar los motion states
    # Buscar el bucle de actualización de posiciones
    for_motions = content.find("for source_id, motion in self.motion_states.items():", update_pos)
    
    if for_motions == -1:
        # Si no existe, buscar dónde añadirlo
        # Buscar antes de _send_osc_update
        osc_update = content.find("self._send_osc_update()", update_pos)
        if osc_update != -1:
            # Insertar código para procesar motion states
            motion_code = """
        # Procesar componentes de movimiento con deltas
        for source_id, motion in self.motion_states.items():
            if hasattr(motion, 'update_with_deltas'):
                deltas = motion.update_with_deltas(dt)
                
                # Aplicar deltas a la posición
                for delta in deltas:
                    if delta.position is not None:
                        self._positions[source_id] += delta.position
                    if delta.orientation is not None:
                        self._orientations[source_id] += delta.orientation
        
"""
            content = content[:osc_update] + motion_code + content[osc_update:]
            print("✅ Código de procesamiento de deltas añadido")

# Guardar
with open(file_path, 'w') as f:
    f.write(content)

print(f"✅ Backup: {backup_path}")
print("✅ Engine actualizado para procesar trayectorias individuales")
'''

with open("fix_engine_update_individual.py", "w") as f:
    f.write(fix_code)

print("\n✅ Script de corrección creado: fix_engine_update_individual.py")
print("📝 Ejecuta: python fix_engine_update_individual.py")