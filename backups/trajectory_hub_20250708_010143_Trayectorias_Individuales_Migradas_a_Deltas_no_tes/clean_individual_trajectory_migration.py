# === clean_individual_trajectory_migration.py ===
# 🔧 Fix: Restaurar backup limpio y migrar correctamente
# ⚡ Evitar problemas de indentación

import os
import shutil
from datetime import datetime

print("🔧 Migración limpia de IndividualTrajectory...")

# Restaurar desde el backup más antiguo que funcionaba
file_path = "trajectory_hub/core/motion_components.py"
good_backup = "trajectory_hub/core/motion_components.py.backup_20250708_003129"

if os.path.exists(good_backup):
    shutil.copy2(good_backup, file_path)
    print("✅ Restaurado desde backup limpio")
else:
    print("❌ No se encontró el backup limpio")
    exit(1)

# Ahora añadir los métodos necesarios correctamente
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Buscar IndividualTrajectory
import_section = '''import numpy as np
from trajectory_hub.core.movement_modes import TrajectoryMovementMode'''

if "from trajectory_hub.core.movement_modes import TrajectoryMovementMode" not in content:
    # Añadir import después de otros imports
    numpy_import = content.find("import numpy as np")
    if numpy_import != -1:
        end_line = content.find("\n", numpy_import)
        content = content[:end_line] + "\nfrom trajectory_hub.core.movement_modes import TrajectoryMovementMode" + content[end_line:]

# Encontrar IndividualTrajectory y añadir métodos
individual_class = content.find("class IndividualTrajectory(MotionComponent, MovementModeMixin):")
if individual_class == -1:
    print("❌ No se encontró IndividualTrajectory")
    exit(1)

# Buscar el final de la clase (siguiente class)
next_class = content.find("\nclass ", individual_class + 1)
if next_class == -1:
    next_class = len(content)

# Insertar métodos antes del final de la clase
methods_to_add = '''
    def update_position(self, dt: float) -> None:
        """Actualiza la posición en la trayectoria según el modo de movimiento."""
        if not self.enabled or self.movement_mode == TrajectoryMovementMode.STOP:
            return
            
        if self.movement_mode == TrajectoryMovementMode.FIX:
            self.position_on_trajectory += self.movement_speed * dt
        elif self.movement_mode == TrajectoryMovementMode.RANDOM:
            import random
            if not hasattr(self, '_last_random_change'):
                self._last_random_change = 0
                self._random_speed = self.movement_speed
            
            self._last_random_change += dt
            if self._last_random_change > 2.0:
                self._random_speed = random.uniform(-2.0, 2.0)
                self._last_random_change = 0
                
            self.position_on_trajectory += self._random_speed * dt
        elif self.movement_mode == TrajectoryMovementMode.VIBRATION:
            vibration = np.sin(self.position_on_trajectory * 20) * 0.5
            self.position_on_trajectory += (self.movement_speed + vibration) * dt
        elif self.movement_mode == TrajectoryMovementMode.SPIN:
            self.position_on_trajectory += self.movement_speed * 5.0 * dt
            
        self.position_on_trajectory = self.position_on_trajectory % 1.0
    
    def _calculate_position_on_trajectory(self, phase: float) -> np.ndarray:
        """Calcula la posición 3D en la trayectoria basada en la fase [0, 1]."""
        t = phase * 2 * np.pi
        
        if self.shape_type == "circle":
            radius = self.shape_params.get('radius', 1.0)
            x = radius * np.cos(t)
            y = radius * np.sin(t)
            z = 0.0
        elif self.shape_type == "spiral":
            radius = self.shape_params.get('radius', 1.0)
            height = self.shape_params.get('height', 2.0)
            turns = self.shape_params.get('turns', 3)
            x = radius * np.cos(t * turns)
            y = radius * np.sin(t * turns)
            z = height * phase
        else:
            x = y = z = 0.0
            
        position = np.array([x, y, z])
        if hasattr(self, 'center'):
            position += self.center
        return position
    
    def calculate_delta(self, state: MotionState, dt: float) -> MotionDelta:
        """Calcula el delta de movimiento para trayectoria individual."""
        delta = MotionDelta()
        
        if not self.enabled or self.movement_mode == TrajectoryMovementMode.STOP:
            return delta
        
        self.update_position(dt)
        new_position = self._calculate_position_on_trajectory(self.position_on_trajectory)
        
        if hasattr(state, 'individual_trajectory_position'):
            delta.position = new_position - state.individual_trajectory_position
        else:
            delta.position = new_position
        
        state.individual_trajectory_position = new_position.copy()
        return delta
'''

# Encontrar dónde insertar (antes del siguiente class o al final)
insert_pos = next_class - 1
content = content[:insert_pos] + methods_to_add + "\n" + content[insert_pos:]

# Guardar
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Métodos añadidos correctamente")

# Test simple
test_code = '''# === test_individual_clean.py ===
from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np

print("🧪 Test limpio de IndividualTrajectory...")

engine = EnhancedTrajectoryEngine(max_sources=3, fps=60)
engine.create_macro("test", [0])

# Configurar manualmente
motion = engine.motion_states[0]
from trajectory_hub.core.motion_components import IndividualTrajectory, TrajectoryMovementMode

traj = IndividualTrajectory()
traj.enabled = True
traj.shape_type = "circle"
traj.shape_params = {"radius": 2.0}
traj.movement_mode = TrajectoryMovementMode.FIX
traj.movement_speed = 1.0
traj.center = np.zeros(3)
motion.active_components['individual_trajectory'] = traj

print("✅ Trayectoria configurada")

# Test calculate_delta
initial_pos = engine._positions[0].copy()
print(f"Posición inicial: {initial_pos}")

# Simular manualmente
for i in range(60):
    deltas = motion.update_with_deltas(1/60)
    for delta in deltas:
        if delta.position is not None:
            engine._positions[0] += delta.position

final_pos = engine._positions[0]
distance = np.linalg.norm(final_pos - initial_pos)

print(f"Posición final: {final_pos}")
print(f"Distancia recorrida: {distance:.3f}")

if distance > 0.1:
    print("\\n✅ ¡IndividualTrajectory funciona con deltas!")
else:
    print("\\n❌ No hubo movimiento")
'''

with open("test_individual_clean.py", "w") as f:
    f.write(test_code)

print("\n📝 Test creado: test_individual_clean.py")
print("🚀 Ejecutando test...")

import subprocess
result = subprocess.run(['python', 'test_individual_clean.py'], 
                      capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("Errores:", result.stderr)