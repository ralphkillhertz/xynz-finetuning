#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
import numpy as np

print("🔍 VERIFICACIÓN CONCENTRATION_FACTOR\n")

engine = EnhancedTrajectoryEngine(max_sources=4, fps=60)
macro_id = engine.create_macro("test", source_count=2, formation="line", spacing=4.0)

print("1. ANTES de set_macro_concentration:")
macro = engine._macros[macro_id]
print(f"   concentration_factor: {getattr(macro, 'concentration_factor', 'NO EXISTE')}")

print("\n2. Llamando set_macro_concentration(0.5)...")
engine.set_macro_concentration(macro_id, 0.5)

print("\n3. DESPUÉS de set_macro_concentration:")
print(f"   concentration_factor: {getattr(macro, 'concentration_factor', 'NO EXISTE')}")

if hasattr(macro, 'concentration_factor'):
    print(f"\n4. Ejecutando step() con factor={macro.concentration_factor}")
    
    # Debug del cálculo
    positions = []
    for sid in macro.source_ids:
        pos = engine._positions[sid].copy()
        positions.append(pos)
        print(f"   Fuente {sid}: {pos}")
    
    center = np.mean(positions, axis=0)
    print(f"   Centro: {center}")
    
    # Simular cálculo
    for i, sid in enumerate(macro.source_ids):
        direction = center - positions[i]
        movement = direction * macro.concentration_factor * 0.016 * 10.0
        new_pos = positions[i] + movement
        print(f"   Fuente {sid} debería ir a: {new_pos}")
    
    # Ejecutar step real
    print("\n5. Ejecutando engine.step()...")
    engine.step()
    
    print("\n6. Posiciones reales después:")
    for sid in macro.source_ids:
        print(f"   Fuente {sid}: {engine._positions[sid]}")
else:
    print("\n❌ concentration_factor sigue sin existir")
    print("   El método set_macro_concentration no está funcionando")
