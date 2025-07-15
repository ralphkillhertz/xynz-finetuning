# === fix_active_components_dict.py ===
# 🔧 Fix: Cambiar active_components de lista a dict
# ⚡ Y encontrar cómo configurar trayectorias realmente

import os
import shutil
from datetime import datetime

def fix_active_components():
    print("🔧 Arreglando active_components para que sea dict...")
    
    # Backup
    file_path = "trajectory_hub/core/motion_components.py"
    backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(file_path, backup_path)
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Buscar SourceMotion.__init__
    init_pos = content.find("class SourceMotion:")
    if init_pos != -1:
        init_method = content.find("def __init__", init_pos)
        if init_method != -1:
            # Buscar active_components = []
            active_comp_pos = content.find("self.active_components = []", init_method)
            if active_comp_pos != -1:
                # Reemplazar con dict
                content = content[:active_comp_pos] + "self.active_components = {}" + content[active_comp_pos + len("self.active_components = []"):]
                print("✅ active_components cambiado a dict")
    
    # Guardar
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Backup: {backup_path}")

def find_trajectory_setup():
    print("\n🔍 Buscando cómo se configuran realmente las trayectorias...")
    
    # Buscar en enhanced_trajectory_engine.py
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    with open(engine_file, 'r') as f:
        content = f.read()
    
    # Buscar set_individual_trajectory
    method_pos = content.find("def set_individual_trajectory")
    if method_pos != -1:
        # Extraer las primeras 20 líneas del método
        lines = content[method_pos:].split('\n')[:20]
        print("\n📄 Método set_individual_trajectory:")
        for line in lines:
            print(f"  {line}")

# Ejecutar fixes
fix_active_components()
find_trajectory_setup()

# Crear test simple
test_code = '''# === test_trajectory_simple.py ===
from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np

print("🧪 Test simple de trayectorias...")

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)

# Crear macro
engine.create_macro("test", [0, 1, 2])

# Debug: ver qué tenemos
print("\\n📋 Estado después de crear macro:")
print(f"  motion_states keys: {list(engine.motion_states.keys())}")
print(f"  Tipo active_components[0]: {type(engine.motion_states[0].active_components)}")

# Intentar crear trayectoria directamente
print("\\n🔧 Creando trayectoria manualmente...")
from trajectory_hub.core.motion_components import IndividualTrajectory

for sid in [0, 1, 2]:
    motion = engine.motion_states[sid]
    
    # Crear componente
    traj = IndividualTrajectory()
    traj.enabled = True
    traj.shape_type = "circle"
    traj.movement_mode = "fix"
    traj.movement_speed = 0.5
    traj.set_trajectory("circle", radius=1.0)
    
    # Añadir al motion
    if isinstance(motion.active_components, dict):
        motion.active_components['individual_trajectory'] = traj
    else:
        # Si es lista, cambiar a dict
        motion.active_components = {'individual_trajectory': traj}
    
    print(f"  ✅ Trayectoria añadida a fuente {sid}")

# Test de movimiento
print("\\n🏃 Test de movimiento...")
initial = engine._positions.copy()

# Simular (sin parámetro dt)
for _ in range(60):
    engine.update()

# Verificar
print("\\n📊 Resultados:")
for sid in [0, 1, 2]:
    dist = np.linalg.norm(engine._positions[sid] - initial[sid])
    print(f"  Fuente {sid}: movió {dist:.3f}")
    
    # Debug del componente
    if sid in engine.motion_states:
        motion = engine.motion_states[sid]
        if 'individual_trajectory' in motion.active_components:
            traj = motion.active_components['individual_trajectory']
            print(f"    Phase: {getattr(traj, 'position_on_trajectory', 0):.3f}")
'''

with open("test_trajectory_simple.py", "w") as f:
    f.write(test_code)

print("\n✅ Test creado: test_trajectory_simple.py")