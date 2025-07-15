# === fix_update_signature.py ===
# 🔧 Fix: Encontrar la firma correcta de update_with_deltas
# ⚡ Y adaptar el código para usarla correctamente

import os

print("🔍 Investigando la firma de update_with_deltas...")

file_path = "trajectory_hub/core/motion_components.py"

with open(file_path, 'r') as f:
    content = f.read()

# Buscar la definición exacta
source_motion_pos = content.find("class SourceMotion:")
update_pos = content.find("def update_with_deltas", source_motion_pos)

if update_pos != -1:
    # Extraer las siguientes líneas para ver la firma completa
    method_end = content.find(":", update_pos)
    next_line = content.find("\n", method_end)
    
    method_signature = content[update_pos:method_end+1]
    print(f"\n📋 Firma actual: {method_signature}")
    
    # Ver las primeras líneas del método
    method_body = content[update_pos:update_pos+500]
    print("\n📄 Primeras líneas del método:")
    for line in method_body.split('\n')[:10]:
        print(f"  {line}")

# Crear test adaptado a la firma correcta
test_code = '''# === test_individual_adapted.py ===
from trajectory_hub import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import IndividualTrajectory, TrajectoryMovementMode
import numpy as np
import time

print("🧪 Test adaptado de IndividualTrajectory...")

# Setup
engine = EnhancedTrajectoryEngine(max_sources=3, fps=60)
engine.create_macro("test", [0, 1, 2])

# Configurar trayectorias
for i, sid in enumerate([0, 1, 2]):
    motion = engine.motion_states[sid]
    traj = IndividualTrajectory()
    traj.enabled = True
    traj.shape_type = "circle"
    traj.shape_params = {"radius": 1.0 + i * 0.5}
    traj.movement_mode = TrajectoryMovementMode.FIX
    traj.movement_speed = 0.5
    traj.center = np.zeros(3)
    motion.active_components['individual_trajectory'] = traj
    print(f"✅ Trayectoria configurada para fuente {sid}")

# Ver qué parámetros espera update_with_deltas
motion = engine.motion_states[0]
print("\\n🔍 Inspeccionando update_with_deltas...")
import inspect
try:
    sig = inspect.signature(motion.update_with_deltas)
    print(f"   Firma: {sig}")
except:
    print("   No se pudo obtener firma")

# Probar diferentes formas de llamarlo
print("\\n🧪 Probando diferentes llamadas...")

# Opción 1: Solo current_time
try:
    current_time = time.time()
    deltas = motion.update_with_deltas(current_time)
    print(f"✅ Funciona con current_time: {len(deltas)} deltas")
except Exception as e:
    print(f"❌ Con current_time: {e}")

# Opción 2: current_time y dt
try:
    current_time = time.time()
    dt = 1/60
    deltas = motion.update_with_deltas(current_time, dt)
    print(f"✅ Funciona con current_time y dt: {len(deltas)} deltas")
except Exception as e:
    print(f"❌ Con current_time y dt: {e}")

# Usar la forma que funcionó
print("\\n🏃 Simulación adaptada...")
initial = {}
for sid in [0, 1, 2]:
    initial[sid] = engine._positions[sid].copy()

# Simular con el método correcto
start_time = time.time()
for frame in range(60):  # 1 segundo
    current_time = start_time + frame/60
    
    for sid in [0, 1, 2]:
        motion = engine.motion_states[sid]
        
        # Intentar con la firma que esperamos
        try:
            # Si espera current_time, calcular dt internamente
            if hasattr(motion.state, 'last_update'):
                dt = current_time - motion.state.last_update
                motion.state.last_update = current_time
            else:
                dt = 1/60
                motion.state.last_update = current_time
            
            # Actualizar componentes manualmente si es necesario
            traj = motion.active_components.get('individual_trajectory')
            if traj and hasattr(traj, 'update_position'):
                # Actualizar posición
                old_phase = traj.position_on_trajectory
                traj.update_position(dt)
                
                # Calcular nueva posición
                if hasattr(traj, '_calculate_position_on_trajectory'):
                    new_pos = traj._calculate_position_on_trajectory(traj.position_on_trajectory)
                    old_pos = traj._calculate_position_on_trajectory(old_phase)
                    
                    # Aplicar delta directamente
                    delta_pos = new_pos - old_pos
                    engine._positions[sid] += delta_pos
                    
        except Exception as e:
            if frame == 0:
                print(f"❌ Error en simulación: {e}")

# Resultados
print("\\n📊 Resultados:")
for sid in [0, 1, 2]:
    dist = np.linalg.norm(engine._positions[sid] - initial[sid])
    status = "✅" if dist > 0.1 else "❌"
    print(f"  Fuente {sid}: {status} Movió {dist:.3f}")

# Si no funciona con deltas, al menos sabemos que el componente funciona
if all(np.linalg.norm(engine._positions[sid] - initial[sid]) > 0.1 for sid in [0, 1, 2]):
    print("\\n✅ ¡Las trayectorias funcionan!")
    print("\\n📝 Nota: Necesitamos adaptar update_with_deltas o crear uno nuevo")
'''

with open("test_individual_adapted.py", "w") as f:
    f.write(test_code)

print("\n✅ Test adaptado creado: test_individual_adapted.py")

# Crear fix alternativo
fix_code = '''# === fix_update_deltas_signature.py ===
import os
import shutil
from datetime import datetime

print("🔧 Creando wrapper para update_with_deltas...")

file_path = "trajectory_hub/core/motion_components.py"
backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(file_path, backup_path)

with open(file_path, 'r') as f:
    content = f.read()

# Añadir un método wrapper que acepte dt
wrapper_code = """
    def update_with_dt(self, dt: float) -> list:
        \"""Wrapper para update_with_deltas que acepta dt directamente.\"""
        import time
        current_time = getattr(self.state, 'last_update', 0) + dt
        self.state.last_update = current_time
        
        # Procesar componentes manualmente
        deltas = []
        
        # Individual trajectory
        if 'individual_trajectory' in self.active_components:
            traj = self.active_components['individual_trajectory']
            if traj and hasattr(traj, 'calculate_delta'):
                delta = traj.calculate_delta(self.state, dt)
                if delta and delta.position is not None:
                    deltas.append(delta)
        
        return deltas
"""

# Insertar después de update_with_deltas
source_motion_pos = content.find("class SourceMotion:")
if source_motion_pos != -1:
    # Buscar un buen lugar para insertar (después de algún método)
    insert_pos = content.find("def get_state", source_motion_pos)
    if insert_pos == -1:
        insert_pos = content.find("def __init__", source_motion_pos)
    
    if insert_pos != -1:
        # Encontrar el final del método
        next_def = content.find("\\n    def ", insert_pos + 1)
        if next_def != -1:
            content = content[:next_def] + wrapper_code + content[next_def:]
            print("✅ Método update_with_dt añadido")

with open(file_path, 'w') as f:
    f.write(content)

print(f"✅ Backup: {backup_path}")
'''

with open("fix_update_deltas_signature.py", "w") as f:
    f.write(fix_code)

print("\n📝 Scripts creados:")
print("   1. test_individual_adapted.py - Test que se adapta a la firma")
print("   2. fix_update_deltas_signature.py - Añade wrapper update_with_dt")