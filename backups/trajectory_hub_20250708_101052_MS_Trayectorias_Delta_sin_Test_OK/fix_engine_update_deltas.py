# === fix_engine_update_deltas.py ===
# 🔧 Fix: Hacer que engine.update() procese deltas automáticamente
# ⚡ No más procesamiento manual en cada test

import os
import shutil
from datetime import datetime

print("🔧 Arreglando engine.update() para procesar deltas automáticamente...")

file_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(file_path, backup_path)

with open(file_path, 'r') as f:
    content = f.read()

# Buscar el método update
update_pos = content.find("def update(self):")
if update_pos == -1:
    print("❌ No se encontró def update(self):")
    exit(1)

print("✅ Método update encontrado")

# Buscar dónde insertar el código de deltas
# Buscar _send_osc_update o el final del método
osc_update_pos = content.find("self._send_osc_update()", update_pos)
if osc_update_pos == -1:
    # Buscar el siguiente método
    next_method = content.find("\n    def ", update_pos + 1)
    insert_pos = next_method if next_method != -1 else len(content)
else:
    insert_pos = osc_update_pos

# Código para procesar deltas
delta_processing = '''
        # Procesar deltas de todos los motion states
        current_time = time.time()
        dt = 1.0 / self.fps if hasattr(self, 'fps') else 1.0 / 60.0
        
        for source_id, motion in self.motion_states.items():
            if hasattr(motion, 'update_with_deltas'):
                try:
                    # Obtener deltas del motion state
                    deltas = motion.update_with_deltas(current_time, dt)
                    
                    # Aplicar cada delta a la posición
                    for delta in deltas:
                        if delta and hasattr(delta, 'position') and delta.position is not None:
                            self._positions[source_id] += delta.position
                        if delta and hasattr(delta, 'orientation') and delta.orientation is not None:
                            if hasattr(self, '_orientations'):
                                self._orientations[source_id] += delta.orientation
                                
                except Exception as e:
                    logger.debug(f"Error procesando deltas para fuente {source_id}: {e}")
        
'''

# Insertar antes de _send_osc_update
content = content[:insert_pos] + delta_processing + content[insert_pos:]

# Asegurar que time está importado
if "import time" not in content:
    import_pos = content.find("import")
    content = content[:import_pos] + "import time\n" + content[import_pos:]

# Guardar
with open(file_path, 'w') as f:
    f.write(content)

print(f"✅ Backup: {backup_path}")
print("✅ engine.update() actualizado para procesar deltas")

# Test automático
test_code = '''# === test_engine_auto_deltas.py ===
from trajectory_hub import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import IndividualTrajectory, TrajectoryMovementMode
import numpy as np

print("🧪 Test de procesamiento AUTOMÁTICO de deltas en engine.update()...")

# Setup
engine = EnhancedTrajectoryEngine(max_sources=3, fps=60)
engine.create_macro("test", [0, 1, 2])

# Configurar trayectorias
shapes = ["circle", "spiral", "figure8"]
for sid, shape in enumerate(shapes):
    motion = engine.motion_states[sid]
    traj = IndividualTrajectory()
    traj.enabled = True
    traj.shape_type = shape
    traj.shape_params = {"radius": 2.0, "scale": 2.0, "height": 2.0}
    traj.movement_mode = TrajectoryMovementMode.FIX
    traj.movement_speed = 0.5
    traj.center = np.zeros(3)
    motion.active_components['individual_trajectory'] = traj
    print(f"✅ {shape} configurado para fuente {sid}")

# Guardar posiciones iniciales
initial = {}
for sid in range(3):
    initial[sid] = engine._positions[sid].copy()

print("\\n🏃 Simulando SIN procesamiento manual de deltas...")
print("   (engine.update() debe hacerlo automáticamente)")

# SOLO llamar a engine.update(), sin procesar deltas manualmente
for frame in range(60):  # 1 segundo
    engine.update()  # ¡Sin parámetros, sin procesamiento manual!
    
    if frame % 20 == 0:
        print(f"\\n  Frame {frame}:")
        for sid, shape in enumerate(shapes):
            pos = engine._positions[sid]
            dist = np.linalg.norm(pos - initial[sid])
            print(f"    {shape}: distancia = {dist:.3f}")

# Verificar resultados
print("\\n📊 RESULTADOS FINALES:")
success = True
for sid, shape in enumerate(shapes):
    final_pos = engine._positions[sid]
    dist = np.linalg.norm(final_pos - initial[sid])
    
    if dist > 0.1:
        print(f"  ✅ {shape}: Se movió {dist:.3f} unidades AUTOMÁTICAMENTE")
    else:
        print(f"  ❌ {shape}: NO se movió (dist={dist:.3f})")
        success = False

if success:
    print("\\n🎉 ¡ÉXITO TOTAL!")
    print("   engine.update() procesa deltas automáticamente")
    print("   No más procesamiento manual en tests")
    print("\\n📝 Próximo paso: Migrar MacroTrajectory a deltas")
else:
    print("\\n❌ El procesamiento automático no funciona")
    print("   Revisar la implementación en engine.update()")
'''

with open("test_engine_auto_deltas.py", "w") as f:
    f.write(test_code)

print("\n✅ Test creado: test_engine_auto_deltas.py")
print("🚀 Ejecutando test...")

import subprocess
result = subprocess.run(['python', 'test_engine_auto_deltas.py'], 
                      capture_output=True, text=True)

# Mostrar resultados
if result.stdout:
    lines = result.stdout.strip().split('\n')
    # Mostrar título y últimas líneas importantes
    print(lines[0])
    for line in lines[-15:]:
        if any(word in line for word in ['Frame', '✅', '❌', 'ÉXITO', 'RESULTADOS']):
            print(line)

if result.stderr and "No se puede crear modulador" not in result.stderr:
    print("\nErrores:", result.stderr)