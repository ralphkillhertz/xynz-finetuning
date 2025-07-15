#!/usr/bin/env python3
"""
🧪 TEST FINAL: Concentración completa
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

print("\n🧪 TEST FINAL DE CONCENTRACIÓN\n")

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)

# Crear macro con fuentes dispersas
macro_id = engine.create_macro("test", source_count=4, formation="grid", spacing=4.0)

# Guardar posiciones iniciales
initial_pos = {}
for sid in range(4):
    if sid in engine._source_motions:
        pos = engine._source_motions[sid].state.position.copy()
        initial_pos[sid] = pos
        print(f"📍 Fuente {sid} inicial: {pos}")

# Aplicar concentración
print("\n🎯 Aplicando concentración factor=0.5...")
engine.set_macro_concentration(macro_id, 0.5)

# Verificar offsets
print("\n🔍 Verificando offsets calculados:")
for sid in range(4):
    if sid in engine._source_motions:
        motion = engine._source_motions[sid]
        offset = motion.concentration_offset
        mag = np.linalg.norm(offset)
        print(f"   Fuente {sid}: offset={offset}, magnitud={mag:.4f}")

# Ejecutar simulación
print("\n🔄 Ejecutando 60 frames...")
for i in range(60):
    engine.step()
    
    # Mostrar progreso cada 20 frames
    if (i + 1) % 20 == 0:
        print(f"   Frame {i+1}")
        # Verificar una posición
        if 0 in engine._source_motions:
            pos = engine._positions[0]
            print(f"      Fuente 0 está en: {pos}")

# Resultados finales
print("\n📊 RESULTADOS FINALES:")
total_movement = 0
for sid in initial_pos:
    if sid in engine._source_motions:
        final_pos = engine._positions[sid]
        movement = np.linalg.norm(final_pos - initial_pos[sid])
        total_movement += movement
        print(f"   Fuente {sid}: movió {movement:.4f} unidades")

avg_movement = total_movement / len(initial_pos) if initial_pos else 0

if avg_movement > 0.1:
    print(f"\n✅ ¡ÉXITO! Movimiento promedio: {avg_movement:.4f}")
    print("🎉 LA CONCENTRACIÓN FUNCIONA CORRECTAMENTE")
    print("\n🚀 Ahora prueba con el controlador interactivo:")
    print("   python trajectory_hub/interface/interactive_controller.py")
else:
    print(f"\n❌ No hubo movimiento suficiente: {avg_movement:.4f}")

print("\n" + "="*60)
