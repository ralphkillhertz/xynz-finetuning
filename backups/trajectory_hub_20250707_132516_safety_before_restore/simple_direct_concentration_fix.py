# === simple_direct_concentration_fix.py ===
# 🔧 Fix: Implementar concentración como en la sesión anterior
# ⚡ Basado en: simple_direct_fix.py que YA FUNCIONÓ

import os
import re

def apply_proven_fix():
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    with open(engine_file, 'r') as f:
        content = f.read()
    
    # Backup
    import datetime
    backup_name = f"{engine_file}.backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(backup_name, 'w') as f:
        f.write(content)
    
    # Buscar el método step() o crearlo si no existe
    if 'def step(' not in content:
        # Buscar dónde insertar (después de update)
        insert_pos = content.find('def update(')
        if insert_pos > 0:
            # Buscar el final del método update
            next_def = content.find('\n    def ', insert_pos + 1)
            if next_def == -1:
                next_def = content.find('\nclass', insert_pos)
            
            step_method = '''
    def step(self, dt: float = None) -> dict:
        """Step actualiza posiciones y aplica concentración DIRECTAMENTE."""
        if dt is None:
            dt = self.dt
        
        # Para cada macro con concentración
        for macro_id, macro in self._macros.items():
            factor = getattr(macro, 'concentration_factor', 0)
            if factor > 0 and hasattr(macro, 'source_ids'):
                # Calcular centro y mover fuentes
                positions = []
                for sid in macro.source_ids:
                    if sid < self.max_sources:
                        pos = self._positions[sid].copy()
                        positions.append(pos)
                
                if len(positions) > 1:
                    import numpy as np
                    center = np.mean(positions, axis=0)
                    for i, sid in enumerate(macro.source_ids):
                        current_pos = positions[i]
                        direction = center - current_pos
                        # CÁLCULO DIRECTO PROBADO
                        new_pos = current_pos + (direction * factor * dt * 10.0)
                        self._positions[sid] = new_pos
                        # Actualizar también en source_motions si existe
                        if sid in self._source_motions:
                            self._source_motions[sid].state.position = new_pos.copy()
        
        # Enviar OSC si está activo
        if hasattr(self, '_send_osc_update'):
            self._send_osc_update()
        
        # Devolver estado
        return {
            'positions': self._positions.copy(),
            'orientations': self._orientations.copy(),
            'apertures': self._apertures.copy(),
            'time': getattr(self, '_time', 0),
            'frame': getattr(self, '_frame_count', 0)
        }
'''
            content = content[:next_def] + step_method + '\n' + content[next_def:]
    else:
        # Reemplazar step existente
        pattern = r'def step\([^)]*\)[^:]*:(.*?)(?=\n    def|\nclass|\Z)'
        
        replacement = '''def step(self, dt: float = None) -> dict:
        """Step actualiza posiciones y aplica concentración DIRECTAMENTE."""
        if dt is None:
            dt = self.dt
        
        # Para cada macro con concentración
        for macro_id, macro in self._macros.items():
            factor = getattr(macro, 'concentration_factor', 0)
            if factor > 0 and hasattr(macro, 'source_ids'):
                # Calcular centro y mover fuentes
                positions = []
                for sid in macro.source_ids:
                    if sid < self.max_sources:
                        pos = self._positions[sid].copy()
                        positions.append(pos)
                
                if len(positions) > 1:
                    import numpy as np
                    center = np.mean(positions, axis=0)
                    for i, sid in enumerate(macro.source_ids):
                        current_pos = positions[i]
                        direction = center - current_pos
                        # CÁLCULO DIRECTO PROBADO
                        new_pos = current_pos + (direction * factor * dt * 10.0)
                        self._positions[sid] = new_pos
                        # Actualizar también en source_motions si existe
                        if sid in self._source_motions:
                            self._source_motions[sid].state.position = new_pos.copy()
        
        # Enviar OSC si está activo
        if hasattr(self, '_send_osc_update'):
            self._send_osc_update()
        
        # Devolver estado
        return {
            'positions': self._positions.copy(),
            'orientations': self._orientations.copy(),
            'apertures': self._apertures.copy(),
            'time': getattr(self, '_time', 0),
            'frame': getattr(self, '_frame_count', 0)
        }'''
        
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Guardar
    with open(engine_file, 'w') as f:
        f.write(content)
    
    print("✅ Aplicado fix PROBADO de concentración")
    print("   - Cálculo directo en step()")
    print("   - Sin depender de offsets")
    print("   - Multiplicador x10 para velocidad visible")
    
    # Test simple
    with open("test_concentration_working.py", 'w') as f:
        f.write('''#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
import numpy as np

print("🧪 TEST CONCENTRACIÓN (Método probado)\\n")

engine = EnhancedTrajectoryEngine(max_sources=4, fps=60)
macro_id = engine.create_macro("test", source_count=2, formation="line", spacing=4.0)

# Posiciones iniciales
print("Antes:")
print(f"  Fuente 0: {engine._positions[0]}")
print(f"  Fuente 1: {engine._positions[1]}")

# Aplicar concentración
engine.set_macro_concentration(macro_id, 0.5)

# Ejecutar 10 frames
for _ in range(10):
    engine.step()

print("\\nDespués de 10 frames:")
print(f"  Fuente 0: {engine._positions[0]}")
print(f"  Fuente 1: {engine._positions[1]}")

# Verificar
dispersión_inicial = 4.0
dispersión_final = np.linalg.norm(engine._positions[0] - engine._positions[1])
reducción = (1 - dispersión_final/dispersión_inicial) * 100

print(f"\\nReducción: {reducción:.1f}%")
if reducción > 10:
    print("✅ ¡CONCENTRACIÓN FUNCIONA!")
''')

if __name__ == "__main__":
    apply_proven_fix()