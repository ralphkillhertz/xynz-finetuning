#!/usr/bin/env python3
"""
🔧 FIX DIRECTO: Implementación manual de concentración
"""

import os
import sys
import numpy as np

# Path setup
current_dir = os.getcwd()
if 'trajectory_hub' in current_dir:
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

os.environ['DISABLE_OSC'] = '1'

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

print("\n🔧 APLICANDO CONCENTRACIÓN MANUALMENTE\n")

# Crear engine y macro
engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)
macro_id = engine.create_macro("test", source_count=4, formation="grid", spacing=4.0)

# Obtener macro
macro = engine._macros[macro_id]

# Calcular centro
positions = []
for sid in macro.source_ids:
    if sid in engine._source_motions:
        pos = engine._source_motions[sid].state.position.copy()
        positions.append(pos)
        print(f"Fuente {sid}: {pos}")

center = np.mean(positions, axis=0)
print(f"\nCentro: {center}")

# Aplicar offsets manualmente
concentration_factor = 0.5
print(f"\nAplicando factor {concentration_factor}...")

for i, sid in enumerate(macro.source_ids):
    if sid in engine._source_motions:
        motion = engine._source_motions[sid]
        
        # Calcular offset
        direction = center - positions[i]
        offset = direction * concentration_factor
        
        # Establecer offset
        motion.concentration_offset = offset
        mag = np.linalg.norm(offset)
        print(f"Fuente {sid}: offset magnitud = {mag:.4f}")

# Simular
print("\n🔄 Ejecutando simulación...")
for i in range(60):
    engine.step()
    
    if (i + 1) % 20 == 0:
        pos0 = engine._positions[0]
        print(f"Frame {i+1}: Fuente 0 en {pos0}")

# Verificar movimiento
print("\n📊 RESULTADO:")
for sid in macro.source_ids:
    if sid in engine._source_motions:
        final_pos = engine._positions[sid]
        initial_pos = positions[sid]
        movement = np.linalg.norm(final_pos - initial_pos)
        print(f"Fuente {sid}: movió {movement:.4f} unidades")

print("\n" + "="*60)
