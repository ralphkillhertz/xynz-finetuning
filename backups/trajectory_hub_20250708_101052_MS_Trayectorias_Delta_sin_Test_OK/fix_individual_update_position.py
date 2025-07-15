# === fix_individual_update_position.py ===
# 🔧 Fix: Añadir método update_position que falta
# ⚡ IndividualTrajectory necesita actualizar su fase

import os
import shutil
from datetime import datetime

print("🔧 Arreglando IndividualTrajectory - añadiendo update_position...")

file_path = "trajectory_hub/core/motion_components.py"
backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(file_path, backup_path)

with open(file_path, 'r') as f:
    content = f.read()

# Buscar la clase IndividualTrajectory
class_pos = content.find("class IndividualTrajectory(MotionComponent, MovementModeMixin):")
if class_pos == -1:
    print("❌ No se encontró IndividualTrajectory")
    exit(1)

# Buscar calculate_delta
calc_delta_pos = content.find("def calculate_delta", class_pos)
if calc_delta_pos == -1:
    print("❌ No se encontró calculate_delta")
    exit(1)

# Insertar update_position antes de calculate_delta
update_position_code = '''
    def update_position(self, dt: float) -> None:
        """Actualiza la posición en la trayectoria según el modo de movimiento."""
        if not self.enabled:
            return
            
        # Actualizar según el modo de movimiento
        if self.movement_mode == TrajectoryMovementMode.STOP:
            return
        elif self.movement_mode == TrajectoryMovementMode.FIX:
            # Movimiento constante
            self.position_on_trajectory += self.movement_speed * dt
        elif self.movement_mode == TrajectoryMovementMode.RANDOM:
            # Cambio aleatorio de velocidad
            import random
            if not hasattr(self, '_last_random_change'):
                self._last_random_change = 0
            
            # Cambiar velocidad cada 2 segundos
            if self._last_random_change > 2.0:
                self.movement_speed = random.uniform(-2.0, 2.0)
                self._last_random_change = 0
            else:
                self._last_random_change += dt
                
            self.position_on_trajectory += self.movement_speed * dt
        elif self.movement_mode == TrajectoryMovementMode.VIBRATION:
            # Vibración sinusoidal
            import numpy as np
            vibration = np.sin(self.position_on_trajectory * 20) * 0.5
            self.position_on_trajectory += (self.movement_speed + vibration) * dt
        elif self.movement_mode == TrajectoryMovementMode.SPIN:
            # Giro rápido
            self.position_on_trajectory += self.movement_speed * 5.0 * dt
            
        # Normalizar para mantener en rango [0, 1]
        self.position_on_trajectory = self.position_on_trajectory % 1.0
'''

# Insertar antes de calculate_delta
content = content[:calc_delta_pos] + update_position_code + "\n" + content[calc_delta_pos:]

# También necesitamos arreglar los imports de TrajectoryMovementMode
# Buscar los imports al principio
imports_start = content.find("from trajectory_hub.core.movement_modes import")
if imports_start == -1:
    # Añadir import si no existe
    enum_import = content.find("from enum import Enum")
    if enum_import != -1:
        import_line = "\nfrom trajectory_hub.core.movement_modes import TrajectoryMovementMode\n"
        content = content[:enum_import] + import_line + content[enum_import:]

# Guardar
with open(file_path, 'w') as f:
    f.write(content)

print(f"✅ Backup: {backup_path}")
print("✅ update_position añadido a IndividualTrajectory")

# Test rápido
test_code = '''# === test_individual_fixed.py ===
from trajectory_hub import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import IndividualTrajectory, TrajectoryMovementMode
import numpy as np

print("🧪 Test con update_position arreglado...")

# Setup
engine = EnhancedTrajectoryEngine(max_sources=3, fps=60)
engine.create_macro("test", [0, 1, 2])

# Configurar manualmente
for sid in [0, 1, 2]:
    motion = engine.motion_states[sid]
    traj = IndividualTrajectory()
    traj.enabled = True
    traj.shape_type = "circle"
    traj.movement_mode = TrajectoryMovementMode.FIX
    traj.movement_speed = 0.5
    traj.set_trajectory("circle", radius=1.0 + sid * 0.5)
    motion.active_components['individual_trajectory'] = traj
    print(f"✅ Trayectoria configurada para fuente {sid}")

# Test directo de update_position
print("\\n🧪 Test directo de componente:")
traj = engine.motion_states[0].active_components['individual_trajectory']
print(f"  Phase inicial: {traj.position_on_trajectory}")
traj.update_position(0.1)
print(f"  Phase después de update: {traj.position_on_trajectory}")

# Test de calculate_delta
delta = traj.calculate_delta(engine.motion_states[0].state, 0.1)
print(f"  Delta calculado: {delta.position}")
print(f"  Phase final: {traj.position_on_trajectory}")

# Test completo con engine (necesita el fix del engine también)
print("\\n🏃 Simulando con engine...")
initial = engine._positions.copy()

# Si engine.update() no procesa deltas, lo hacemos manualmente por ahora
for i in range(60):
    dt = 1/60
    # Procesar cada motion manualmente
    for sid in [0, 1, 2]:
        motion = engine.motion_states[sid]
        deltas = motion.update_with_deltas(dt)
        for delta in deltas:
            if delta.position is not None:
                engine._positions[sid] += delta.position

# Resultados
print("\\n📊 Resultados:")
for sid in [0, 1, 2]:
    dist = np.linalg.norm(engine._positions[sid] - initial[sid])
    status = "✅" if dist > 0.01 else "❌"
    print(f"  Fuente {sid}: {status} Movió {dist:.3f}")

if any(np.linalg.norm(engine._positions[sid] - initial[sid]) > 0.01 for sid in [0, 1, 2]):
    print("\\n🎉 ¡Las trayectorias individuales funcionan!")
    print("\\n⚠️ Ahora ejecuta: python fix_engine_update_individual.py")
    print("    para que engine.update() procese automáticamente los deltas")
'''

with open("test_individual_fixed.py", "w") as f:
    f.write(test_code)

print("\n✅ Test creado: test_individual_fixed.py")