# === add_engine_update_method_fixed.py ===
import os
import shutil
from datetime import datetime
import time

print("🔧 Añadiendo método update() a EnhancedTrajectoryEngine...")

file_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(file_path, backup_path)

with open(file_path, 'r') as f:
    content = f.read()

# Buscar dónde insertar el método update
send_osc_pos = content.find("def _send_osc_update(self):")
if send_osc_pos == -1:
    print("❌ No se encontró _send_osc_update")
    exit(1)

# Método update completo
update_method = '''
    def update(self):
        """Actualiza todas las fuentes procesando deltas de sus componentes."""
        # Calcular dt basado en fps
        current_time = time.time()
        if not hasattr(self, '_last_update_time'):
            self._last_update_time = current_time
            dt = 1.0 / self.fps
        else:
            dt = current_time - self._last_update_time
            self._last_update_time = current_time
        
        # Procesar deltas de todos los motion states
        for source_id, motion in self.motion_states.items():
            if hasattr(motion, 'update_with_deltas'):
                try:
                    # Obtener deltas del motion state
                    deltas = motion.update_with_deltas(current_time, dt)
                    
                    # Aplicar cada delta a la posición
                    for delta in deltas:
                        if delta and hasattr(delta, 'position') and delta.position is not None:
                            # Asegurar que source_id es válido
                            if source_id < len(self._positions):
                                self._positions[source_id] += delta.position
                            
                        if delta and hasattr(delta, 'orientation') and delta.orientation is not None:
                            if hasattr(self, '_orientations') and source_id < len(self._orientations):
                                self._orientations[source_id] += delta.orientation
                                
                except Exception as e:
                    if hasattr(self, 'logger'):
                        self.logger.debug(f"Error procesando deltas para fuente {source_id}: {e}")
                    else:
                        print(f"Error procesando deltas para fuente {source_id}: {e}")
        
        # Incrementar frame count
        if hasattr(self, '_frame_count'):
            self._frame_count += 1
        
        # Enviar actualizaciones OSC si está configurado
        if hasattr(self, '_send_osc_update'):
            self._send_osc_update()
'''

# Insertar antes de _send_osc_update
content = content[:send_osc_pos] + update_method + "\n" + content[send_osc_pos:]

# Asegurar imports necesarios
if "import time" not in content:
    # Añadir después de otros imports
    import_pos = content.find("import numpy")
    if import_pos != -1:
        end_line = content.find("\n", import_pos)
        content = content[:end_line] + "\nimport time" + content[end_line:]

# Guardar
with open(file_path, 'w') as f:
    f.write(content)

print(f"✅ Backup: {backup_path}")
print("✅ Método update() añadido a EnhancedTrajectoryEngine")

# Crear test
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
    for line in lines:
        if any(word in line for word in ['Test', 'Frame', '✅', '❌', 'ÉXITO', 'RESULTADOS', 'configurado']):
            print(line)

if result.stderr and "No se puede crear modulador" not in result.stderr:
    print("\nErrores:", result.stderr)