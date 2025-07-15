# === fix_calculate_position.py ===
# 🔧 Fix: Añadir método _calculate_position_on_trajectory
# ⚡ Calcula la posición 3D en la trayectoria

import os
import shutil
from datetime import datetime
import numpy as np

print("🔧 Añadiendo _calculate_position_on_trajectory...")

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

# Buscar calculate_delta para insertar antes
calc_delta_pos = content.find("def calculate_delta", class_pos)
if calc_delta_pos == -1:
    print("❌ No se encontró calculate_delta")
    exit(1)

# Método _calculate_position_on_trajectory
calculate_method = '''
    def _calculate_position_on_trajectory(self, phase: float) -> np.ndarray:
        """
        Calcula la posición 3D en la trayectoria basada en la fase [0, 1].
        """
        t = phase * 2 * np.pi  # Convertir a radianes
        
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
        elif self.shape_type == "lissajous":
            a = self.shape_params.get('a', 3)
            b = self.shape_params.get('b', 2)
            delta = self.shape_params.get('delta', np.pi/2)
            scale = self.shape_params.get('scale', 1.0)
            x = scale * np.sin(a * t + delta)
            y = scale * np.sin(b * t)
            z = scale * 0.5 * np.sin((a + b) * t)
        elif self.shape_type == "figure8":
            scale = self.shape_params.get('scale', 2.0)
            x = scale * np.sin(t)
            y = scale * np.sin(t) * np.cos(t)
            z = 0.0
        elif self.shape_type == "square":
            size = self.shape_params.get('size', 2.0)
            # Mapear fase a los 4 lados del cuadrado
            side = int(phase * 4)
            t_side = (phase * 4) % 1.0
            
            if side == 0:  # Derecha
                x = size/2
                y = size * (t_side - 0.5)
                z = 0.0
            elif side == 1:  # Arriba
                x = size/2 - size * t_side
                y = size/2
                z = 0.0
            elif side == 2:  # Izquierda
                x = -size/2
                y = size/2 - size * t_side
                z = 0.0
            else:  # Abajo
                x = -size/2 + size * t_side
                y = -size/2
                z = 0.0
        else:
            # Default: punto estático
            x = y = z = 0.0
            
        position = np.array([x, y, z])
        
        # Aplicar centro si existe
        if hasattr(self, 'center'):
            position += self.center
            
        return position
'''

# Insertar antes de calculate_delta
content = content[:calc_delta_pos] + calculate_method + "\n" + content[calc_delta_pos:]

# Guardar
with open(file_path, 'w') as f:
    f.write(content)

print(f"✅ Backup: {backup_path}")
print("✅ _calculate_position_on_trajectory añadido")

# Test completo
print("\n🧪 Ejecutando test completo...")

test_code = '''# === test_individual_complete.py ===
from trajectory_hub import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import IndividualTrajectory, TrajectoryMovementMode
import numpy as np

print("🧪 Test COMPLETO de IndividualTrajectory con deltas...")

# Setup
engine = EnhancedTrajectoryEngine(max_sources=3, fps=60)
engine.create_macro("test", [0, 1, 2])

# Configurar manualmente con diferentes formas
shapes = ["circle", "spiral", "figure8"]
for i, (sid, shape) in enumerate(zip([0, 1, 2], shapes)):
    motion = engine.motion_states[sid]
    traj = IndividualTrajectory()
    traj.enabled = True
    traj.shape_type = shape
    traj.shape_params = {"radius": 1.0 + i*0.5, "scale": 1.0}
    traj.movement_mode = TrajectoryMovementMode.FIX
    traj.movement_speed = 0.5
    traj.center = np.array([0., 0., 0.])  # Centro en origen
    motion.active_components['individual_trajectory'] = traj
    print(f"✅ {shape} configurado para fuente {sid}")

# Test directo del componente
print("\\n🔬 Test directo del componente:")
traj = engine.motion_states[0].active_components['individual_trajectory']
print(f"  Phase inicial: {traj.position_on_trajectory:.3f}")

# Test _calculate_position_on_trajectory
pos = traj._calculate_position_on_trajectory(0.25)  # 1/4 del círculo
print(f"  Posición en fase 0.25: {pos}")

# Test calculate_delta
delta = traj.calculate_delta(engine.motion_states[0].state, 0.1)
print(f"  Delta calculado: {delta.position}")
print(f"  Phase después: {traj.position_on_trajectory:.3f}")

# Guardar posiciones iniciales
initial = {}
for sid in [0, 1, 2]:
    initial[sid] = engine._positions[sid].copy()

# IMPORTANTE: Actualizar engine para que procese deltas
print("\\n🏃 Simulando movimiento...")
print("  (Procesando deltas manualmente por ahora)")

for frame in range(120):  # 2 segundos
    dt = 1/60
    
    # Procesar deltas manualmente
    for sid in [0, 1, 2]:
        motion = engine.motion_states[sid]
        deltas = motion.update_with_deltas(dt)
        
        # Aplicar deltas
        for delta in deltas:
            if delta.position is not None:
                engine._positions[sid] += delta.position
    
    # Mostrar progreso
    if frame % 30 == 0:
        print(f"\\n  T = {frame/60:.1f}s:")
        for sid, shape in zip([0, 1, 2], shapes):
            pos = engine._positions[sid]
            dist = np.linalg.norm(pos - initial[sid])
            print(f"    {shape}: pos={pos}, dist={dist:.3f}")

# Resultados finales
print("\\n📊 RESULTADOS FINALES:")
all_moved = True
for sid, shape in zip([0, 1, 2], shapes):
    final_pos = engine._positions[sid]
    dist = np.linalg.norm(final_pos - initial[sid])
    
    if dist > 0.01:
        print(f"  ✅ {shape} (fuente {sid}): Se movió {dist:.3f} unidades")
    else:
        print(f"  ❌ {shape} (fuente {sid}): NO se movió")
        all_moved = False

if all_moved:
    print("\\n🎉 ¡ÉXITO TOTAL! IndividualTrajectory funciona con deltas!")
    print("\\n⚠️ Siguiente paso: python fix_engine_update_individual.py")
    print("   Para que engine.update() procese automáticamente los deltas")
else:
    print("\\n❌ Algunas trayectorias no funcionaron")
'''

with open("test_individual_complete.py", "w") as f:
    f.write(test_code)

print("✅ Test completo creado: test_individual_complete.py")

# Ejecutar el test
import subprocess
result = subprocess.run(['python', 'test_individual_complete.py'], 
                      capture_output=True, text=True)

if result.stdout:
    print("\n" + result.stdout)
if result.stderr:
    print("\nErrores:", result.stderr)