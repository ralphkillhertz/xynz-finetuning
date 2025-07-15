#!/usr/bin/env python3
"""
🔧 ARREGLAR FIRMA DE ENGINE.UPDATE()
"""

import os
import re

print("🔧 ARREGLANDO engine.update()...")

engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"

with open(engine_file, 'r') as f:
    content = f.read()

# Buscar def update(self):
if 'def update(self):' in content:
    print("✅ Encontrado update(self), cambiando a update(self, dt=None)")
    content = content.replace('def update(self):', 'def update(self, dt=None):')
    
    # Añadir manejo de dt si no existe
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'def update(self, dt=None):' in line:
            # Ver si las siguientes líneas manejan dt
            if i+1 < len(lines) and 'if dt is None:' not in lines[i+1]:
                # Insertar manejo de dt
                indent = '        '
                lines.insert(i+1, f'{indent}if dt is None:')
                lines.insert(i+2, f'{indent}    dt = 1.0 / self.fps')
                break
    
    content = '\n'.join(lines)
    
    # Guardar
    with open(engine_file, 'w') as f:
        f.write(content)
    
    print("✅ engine.update() ahora acepta dt")
else:
    print("❓ No se encontró def update(self):")
    print("   Verificando manualmente...")
