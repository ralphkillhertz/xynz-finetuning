# === fix_add_step_method.py ===
# Añade método step() que faltaba

import os
from datetime import datetime

def add_step_method():
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    with open(engine_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    backup_path = f"{engine_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Buscar dónde insertar (después de update)
    insert_pos = content.find('def update(')
    if insert_pos > -1:
        # Buscar el final del método update
        next_def = content.find('\n    def ', insert_pos + 10)
        if next_def > -1:
            insert_pos = next_def
        else:
            insert_pos = len(content)
    else:
        # Después de __init__
        insert_pos = content.find('def __init__')
        next_def = content.find('\n    def ', insert_pos + 10)
        if next_def > -1:
            insert_pos = next_def
    
    # Método step
    step_method = """
    def step(self) -> None:
        """Ejecuta un paso de simulación"""
        if hasattr(self, 'update'):
            self.update()
        else:
            # Implementación directa si no hay update
            if not self.running:
                return
            
            current_time = time.time()
            dt = 1.0 / self._update_rate
            
            # Sistema de deltas
            all_deltas = []
            
            for source_id, motion in self.motion_states.items():
                if hasattr(motion, 'update_with_deltas'):
                    deltas = motion.update_with_deltas(current_time, dt)
                    if deltas:
                        all_deltas.extend(deltas)
            
            # Aplicar deltas
            for delta in all_deltas:
                if delta.source_id < len(self._positions):
                    if delta.position is not None:
                        self._positions[delta.source_id] += delta.position
"""
    
    # Insertar
    content = content[:insert_pos] + step_method + content[insert_pos:]
    
    # Añadir import time si no existe
    if 'import time' not in content:
        content = 'import time\n' + content
    
    with open(engine_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Método step() añadido")

if __name__ == "__main__":
    add_step_method()
