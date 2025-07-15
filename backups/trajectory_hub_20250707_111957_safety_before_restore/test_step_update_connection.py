#!/usr/bin/env python3
"""
🧪 TEST: Verificar que step() actualiza las fuentes
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

print("\n🧪 TEST DE ENGINE.STEP() → MOTION.UPDATE()\n")

# Crear engine y macro
engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)
macro_id = engine.create_macro("test", source_count=4, formation="line", spacing=2.0)

# Posiciones iniciales
print("📍 POSICIONES INICIALES:")
for i in range(4):
    if i in engine._source_motions:
        pos = engine._source_motions[i].get_position()
        print(f"   Fuente {i}: {pos}")

# Aplicar concentración
print("\n🎯 APLICANDO CONCENTRACIÓN (factor=0.1)...")
engine.set_macro_concentration(macro_id, 0.1)

# Verificar offsets
print("\n🔍 VERIFICANDO OFFSETS:")
for i in range(4):
    if i in engine._source_motions:
        motion = engine._source_motions[i]
        offset = motion.concentration_offset
        print(f"   Fuente {i} offset: {offset}")

# Llamar step() varias veces
print("\n🔄 LLAMANDO ENGINE.STEP() 30 VECES...")
for _ in range(30):
    state = engine.step()

# Posiciones finales
print("\n📍 POSICIONES FINALES:")
movimientos = []
for i in range(4):
    if i in engine._source_motions:
        pos = engine._source_motions[i].get_position()
        inicial = engine._source_motions[i].state.position - engine._source_motions[i].concentration_offset
        movimiento = np.linalg.norm(pos - inicial)
        movimientos.append(movimiento)
        print(f"   Fuente {i}: {pos}")
        print(f"      Movimiento: {movimiento:.4f}")

# Verificar
if all(m > 0.01 for m in movimientos):
    print("\n✅ ¡ÉXITO! Las fuentes se están moviendo")
    print("\n🎉 LA CONCENTRACIÓN FUNCIONA CORRECTAMENTE")
else:
    print("\n❌ Las fuentes NO se mueven")
    print("⚠️  Revisar la implementación de step()")

print("\n" + "="*60)
