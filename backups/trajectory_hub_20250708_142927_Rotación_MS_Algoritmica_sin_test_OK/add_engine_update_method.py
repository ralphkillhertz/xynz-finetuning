# === add_engine_update_method.py ===
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
# Después de __init__ o antes de _send_osc_update
send_osc_pos = content.find("def _send_osc_update(self):")
if send_osc_pos == -1:
    print("❌ No se encontró _send_osc_update")
    exit(1)

# Método update completo
update_method = """
    def update(self):
        """
        Actualiza todas las fuentes procesando deltas de sus componentes.
        Este es el método principal que debe llamarse en cada frame.
        """
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
        
        # Enviar actualizaciones OSC si está configurado
        if hasattr(self, '_send_osc_update'):
            self._send_osc_update()
"""

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
print("\n📝 Ahora el engine tiene un método update() que:")
print("   - Calcula dt automáticamente")
print("   - Procesa deltas de todos los motion_states")
print("   - Aplica deltas a _positions")
print("   - Envía actualizaciones OSC")
