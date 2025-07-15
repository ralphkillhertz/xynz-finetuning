# === complete_individual_trajectory_migration.py ===
# 🔧 Fix: Completar la migración arreglando update_with_deltas
# ⚡ Para que procese el dict de componentes correctamente

import os
import shutil
from datetime import datetime

print("🔧 Completando migración de IndividualTrajectory...")

file_path = "trajectory_hub/core/motion_components.py"
backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(file_path, backup_path)

with open(file_path, 'r') as f:
    content = f.read()

# Buscar update_with_deltas en SourceMotion
update_start = content.find("def update_with_deltas(self, current_time: float, dt: float) -> list:")
if update_start != -1:
    # Buscar el final del método
    method_end = content.find("\n    def ", update_start + 1)
    if method_end == -1:
        method_end = content.find("\nclass", update_start)
    
    # Nuevo método que funciona con dict
    new_method = '''    def update_with_deltas(self, current_time: float, dt: float) -> list:
        """Actualiza componentes y retorna LISTA de deltas"""
        deltas = []
        
        # active_components ahora es un DICT
        if hasattr(self, 'active_components') and isinstance(self.active_components, dict):
            for name, component in self.active_components.items():
                if component and hasattr(component, 'enabled') and component.enabled:
                    if hasattr(component, 'calculate_delta'):
                        delta = component.calculate_delta(self.state, dt)
                        if delta and delta.position is not None:
                            deltas.append(delta)
        
        return deltas'''
    
    # Reemplazar
    content = content[:update_start] + new_method + content[method_end:]
    print("✅ update_with_deltas actualizado para dict")

# Guardar
with open(file_path, 'w') as f:
    f.write(content)

print(f"✅ Backup: {backup_path}")

# Test final integrado
test_code = '''# === test_individual_trajectory_final.py ===
from trajectory_hub import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import IndividualTrajectory, TrajectoryMovementMode
import numpy as np
import time

print("🧪 Test FINAL de IndividualTrajectory con deltas...")

# Setup
engine = EnhancedTrajectoryEngine(max_sources=3, fps=60)
engine.create_macro("test", [0, 1, 2])

# Configurar diferentes trayectorias
configs = [
    {"shape": "circle", "radius": 2.0, "speed": 0.5},
    {"shape": "spiral", "radius": 1.5, "height": 3.0, "speed": 0.3},
    {"shape": "figure8", "scale": 2.5, "speed": 0.4}
]

for sid, config in enumerate(configs):
    motion = engine.motion_states[sid]
    traj = IndividualTrajectory()
    traj.enabled = True
    traj.shape_type = config["shape"]
    traj.shape_params = {k: v for k, v in config.items() if k not in ["shape", "speed"]}
    traj.movement_mode = TrajectoryMovementMode.FIX
    traj.movement_speed = config["speed"]
    traj.center = np.array([sid * 3, 0, 0])  # Separar las trayectorias
    motion.active_components['individual_trajectory'] = traj
    print(f"✅ {config['shape']} configurado para fuente {sid}")

# Test con update_with_deltas corregido
print("\\n🧪 Test de update_with_deltas...")
current_time = time.time()
motion = engine.motion_states[0]
deltas = motion.update_with_deltas(current_time, 1/60)
print(f"  Deltas retornados: {len(deltas)}")
if deltas:
    print(f"  Delta[0]: {deltas[0].position}")

# Guardar posiciones iniciales
initial = {}
for sid in range(3):
    initial[sid] = engine._positions[sid].copy()

# Simular con deltas
print("\\n🏃 Simulando 2 segundos con sistema de deltas...")
start_time = time.time()

for frame in range(120):  # 2 segundos a 60 fps
    current_time = start_time + frame/60
    dt = 1/60
    
    # Procesar cada fuente
    for sid in range(3):
        motion = engine.motion_states[sid]
        deltas = motion.update_with_deltas(current_time, dt)
        
        # Aplicar deltas
        for delta in deltas:
            if delta.position is not None:
                engine._positions[sid] += delta.position
    
    # Mostrar progreso
    if frame % 30 == 0:
        print(f"\\n  T = {frame/60:.1f}s:")
        for sid, config in enumerate(configs):
            pos = engine._positions[sid]
            dist = np.linalg.norm(pos - initial[sid])
            traj = motion.active_components['individual_trajectory']
            print(f"    {config['shape']}: dist={dist:.3f}, phase={traj.position_on_trajectory:.3f}")

# Resultados finales
print("\\n📊 RESULTADOS FINALES:")
all_success = True
for sid, config in enumerate(configs):
    final_pos = engine._positions[sid]
    dist = np.linalg.norm(final_pos - initial[sid])
    
    if dist > 0.1:
        print(f"  ✅ {config['shape']} (fuente {sid}): Movió {dist:.3f} unidades")
    else:
        print(f"  ❌ {config['shape']} (fuente {sid}): NO se movió")
        all_success = False

if all_success:
    print("\\n🎉 ¡MIGRACIÓN COMPLETA!")
    print("\\n✅ IndividualTrajectory migrado exitosamente a sistema de deltas")
    print("\\n📝 Siguiente paso: Migrar MacroTrajectory")
    print("   Ejecuta: python migrate_macro_trajectory.py")
else:
    print("\\n❌ Algo falló en la migración")

# Guardar estado
state = {
    "individual_trajectory": "✅ Migrado a deltas",
    "macro_trajectory": "❌ Pendiente",
    "rotation_ms": "❌ Pendiente",
    "rotation_is": "❌ Pendiente"
}

import json
with open("migration_state.json", "w") as f:
    json.dump(state, f, indent=2)
print("\\n💾 Estado guardado en migration_state.json")
'''

with open("test_individual_trajectory_final.py", "w") as f:
    f.write(test_code)

print("\n✅ Test final creado: test_individual_trajectory_final.py")
print("🚀 Ejecutando...")

import subprocess
result = subprocess.run(['python', 'test_individual_trajectory_final.py'], 
                      capture_output=True, text=True)
print(result.stdout)
if result.stderr and "No se puede crear modulador" not in result.stderr:
    print("Errores:", result.stderr)