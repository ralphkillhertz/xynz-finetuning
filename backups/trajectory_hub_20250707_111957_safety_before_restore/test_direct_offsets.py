#!/usr/bin/env python3
"""
🧪 TEST DIRECTO: Offsets en posiciones
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

print("\n🧪 TEST DIRECTO DE OFFSETS\n")

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=2, fps=60)

# Crear 2 fuentes
engine.create_source(0, "Test0", position=np.array([-2.0, 0.0, 0.0]))
engine.create_source(1, "Test1", position=np.array([2.0, 0.0, 0.0]))

# Crear macro
macro_id = engine.create_macro("test", source_count=0)
engine._macros[macro_id].source_ids = {0, 1}

print("📍 Posiciones iniciales:")
print(f"   Fuente 0: {engine._positions[0]}")
print(f"   Fuente 1: {engine._positions[1]}")

# Aplicar concentración
print("\n🎯 Aplicando concentración 0.5...")
engine.set_macro_concentration(macro_id, 0.5)

# Verificar offsets
if 0 in engine._source_motions:
    offset0 = engine._source_motions[0].concentration_offset
    offset1 = engine._source_motions[1].concentration_offset
    print(f"\n🔍 Offsets calculados:")
    print(f"   Fuente 0: {offset0}")
    print(f"   Fuente 1: {offset1}")

# Llamar a step o update
print("\n🔄 Actualizando...")
if hasattr(engine, 'step'):
    engine.step()
elif hasattr(engine, 'update'):
    engine.update(engine.dt)

print("\n📍 Posiciones después:")
print(f"   Fuente 0: {engine._positions[0]}")
print(f"   Fuente 1: {engine._positions[1]}")

# Verificar movimiento
mov0 = np.linalg.norm(engine._positions[0] - np.array([-2.0, 0.0, 0.0]))
mov1 = np.linalg.norm(engine._positions[1] - np.array([2.0, 0.0, 0.0]))

if mov0 > 0.01 or mov1 > 0.01:
    print(f"\n✅ ¡ÉXITO! Las fuentes se movieron:")
    print(f"   Fuente 0: {mov0:.4f}")
    print(f"   Fuente 1: {mov1:.4f}")
    print("\n🎉 LA CONCENTRACIÓN FUNCIONA!")
else:
    print(f"\n❌ Las fuentes NO se movieron")
    
    # Aplicar offset manualmente para verificar
    print("\n🔧 Aplicando offsets manualmente...")
    if 0 in engine._source_motions:
        motion0 = engine._source_motions[0]
        motion1 = engine._source_motions[1]
        
        engine._positions[0] = motion0.state.position + motion0.concentration_offset
        engine._positions[1] = motion1.state.position + motion1.concentration_offset
        
        print(f"   Fuente 0: {engine._positions[0]}")
        print(f"   Fuente 1: {engine._positions[1]}")
        
        print("\n💡 Los offsets funcionan manualmente")
        print("   El problema está en update() o step()")

print("\n" + "="*60)
