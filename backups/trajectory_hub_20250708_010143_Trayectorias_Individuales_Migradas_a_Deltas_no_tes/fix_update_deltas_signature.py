# === fix_update_deltas_signature.py ===
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
        """Wrapper para update_with_deltas que acepta dt directamente."""
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
        next_def = content.find("\n    def ", insert_pos + 1)
        if next_def != -1:
            content = content[:next_def] + wrapper_code + content[next_def:]
            print("✅ Método update_with_dt añadido")

with open(file_path, 'w') as f:
    f.write(content)

print(f"✅ Backup: {backup_path}")
