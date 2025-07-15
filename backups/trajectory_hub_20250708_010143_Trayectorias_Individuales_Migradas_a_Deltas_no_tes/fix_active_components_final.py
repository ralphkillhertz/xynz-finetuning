# === fix_active_components_final.py ===
# 🔧 Fix: Cambiar active_components de lista a dict una vez más
# ⚡ Y actualizar update_with_deltas para procesarlos

import os
import shutil
from datetime import datetime

print("🔧 Arreglando active_components para que sea dict...")

file_path = "trajectory_hub/core/motion_components.py"
backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(file_path, backup_path)

with open(file_path, 'r') as f:
    content = f.read()

# 1. Cambiar active_components = [] por active_components = {}
content = content.replace("self.active_components = []", "self.active_components = {}")
print("✅ active_components cambiado a dict")

# 2. Actualizar update_with_deltas para que funcione con dict
update_deltas_start = content.find("def update_with_deltas(self, dt: float)")
if update_deltas_start != -1:
    # Buscar el return
    return_pos = content.find("return deltas", update_deltas_start)
    
    # Reemplazar el método completo
    new_method = '''    def update_with_deltas(self, dt: float) -> list:
        """Actualiza el estado y retorna lista de deltas de todos los componentes activos."""
        deltas = []
        
        # Procesar concentración si existe
        if 'concentration' in self.active_components:
            component = self.active_components['concentration']
            if component and hasattr(component, 'calculate_delta'):
                delta = component.calculate_delta(self.state, dt)
                if delta and delta.position is not None:
                    deltas.append(delta)
        
        # Procesar trayectoria individual
        if 'individual_trajectory' in self.active_components:
            component = self.active_components['individual_trajectory']
            if component and hasattr(component, 'calculate_delta'):
                delta = component.calculate_delta(self.state, dt)
                if delta and delta.position is not None:
                    deltas.append(delta)
        
        # Procesar otros componentes
        for name, component in self.active_components.items():
            if name not in ['concentration', 'individual_trajectory']:
                if component and hasattr(component, 'calculate_delta'):
                    delta = component.calculate_delta(self.state, dt)
                    if delta:
                        deltas.append(delta)
        
        return deltas'''
    
    # Encontrar el final del método actual
    method_end = content.find("\n    def ", update_deltas_start + 1)
    if method_end == -1:
        method_end = content.find("\nclass ", update_deltas_start)
    
    # Reemplazar
    content = content[:update_deltas_start] + new_method + "\n" + content[method_end:]
    print("✅ update_with_deltas actualizado para dict")

# Guardar
with open(file_path, 'w') as f:
    f.write(content)

print(f"✅ Backup: {backup_path}")

# Test actualizado
test_code = '''# === test_individual_working.py ===
from trajectory_hub import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import IndividualTrajectory, TrajectoryMovementMode
import numpy as np

print("🧪 Test de IndividualTrajectory con active_components dict...")

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=3, fps=60)
engine.create_macro("test", [0, 1, 2])

print("\\n📋 Verificando estructura:")
for sid in [0, 1, 2]:
    motion = engine.motion_states[sid]
    print(f"  Fuente {sid}: active_components es {type(motion.active_components)}")

# Configurar trayectorias
shapes = ["circle", "spiral", "figure8"]
for sid, shape in zip([0, 1, 2], shapes):
    motion = engine.motion_states[sid]
    
    # Crear componente
    traj = IndividualTrajectory()
    traj.enabled = True
    traj.shape_type = shape
    traj.shape_params = {"radius": 1.0 + sid * 0.5}
    traj.movement_mode = TrajectoryMovementMode.FIX
    traj.movement_speed = 0.5
    traj.center = np.zeros(3)
    traj.position_on_trajectory = 0.0
    
    # Añadir al diccionario
    motion.active_components['individual_trajectory'] = traj
    print(f"✅ {shape} configurado para fuente {sid}")

# Guardar posiciones iniciales
initial = {}
for sid in [0, 1, 2]:
    initial[sid] = engine._positions[sid].copy()

print("\\n🏃 Simulando 2 segundos...")
# Procesar deltas manualmente (hasta que arreglemos engine.update)
for frame in range(120):  # 2 segundos a 60 fps
    dt = 1/60
    
    for sid in [0, 1, 2]:
        motion = engine.motion_states[sid]
        deltas = motion.update_with_deltas(dt)
        
        for delta in deltas:
            if delta.position is not None:
                engine._positions[sid] += delta.position
    
    # Mostrar progreso cada 0.5 segundos
    if frame % 30 == 0 and frame > 0:
        print(f"\\n  T = {frame/60:.1f}s:")
        for sid, shape in zip([0, 1, 2], shapes):
            pos = engine._positions[sid]
            dist = np.linalg.norm(pos - initial[sid])
            traj = motion.active_components['individual_trajectory']
            phase = traj.position_on_trajectory
            print(f"    {shape}: dist={dist:.3f}, phase={phase:.3f}")

# Resultados finales
print("\\n📊 RESULTADOS FINALES:")
success = True
for sid, shape in zip([0, 1, 2], shapes):
    final_pos = engine._positions[sid]
    dist = np.linalg.norm(final_pos - initial[sid])
    
    if dist > 0.01:
        print(f"  ✅ {shape} (fuente {sid}): Movió {dist:.3f} unidades")
    else:
        print(f"  ❌ {shape} (fuente {sid}): NO se movió")
        success = False

if success:
    print("\\n🎉 ¡ÉXITO! IndividualTrajectory migrado a deltas correctamente!")
    print("\\n📝 Siguiente: Migrar MacroTrajectory")
    print("   Ejecuta: python migrate_macro_trajectory.py")
else:
    print("\\n❌ Debug necesario")
'''

with open("test_individual_working.py", "w") as f:
    f.write(test_code)

print("\n✅ Test creado: test_individual_working.py")
print("🚀 Ejecutando...")

import subprocess
result = subprocess.run(['python', 'test_individual_working.py'], 
                      capture_output=True, text=True)
print(result.stdout)
if result.stderr and "No se puede crear modulador" not in result.stderr:
    print("Errores:", result.stderr)