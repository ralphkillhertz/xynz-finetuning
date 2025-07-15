#!/usr/bin/env python3
"""Debug de create_macro"""

from trajectory_hub import EnhancedTrajectoryEngine

engine = EnhancedTrajectoryEngine()

# Probar create_macro
print("🔍 Probando create_macro...")
result = engine.create_macro("test_macro", source_count=2)
print(f"Resultado: {result}")
print(f"Tipo: {type(result)}")

# Ver qué se creó
if hasattr(engine, '_macros'):
    print(f"\nMacros existentes: {list(engine._macros.keys())}")
    if result in engine._macros:
        macro = engine._macros[result]
        print(f"Macro '{result}':")
        print(f"  source_ids: {macro.source_ids if hasattr(macro, 'source_ids') else 'no tiene'}")
        print(f"  tipo: {type(macro)}")

# Ver motion_states
if hasattr(engine, 'motion_states'):
    print(f"\nMotion states: {list(engine.motion_states.keys())}")

# Ver posiciones
print(f"\nPosiciones no-cero:")
for i in range(10):
    if engine._positions[i].any():
        print(f"  Posición {i}: {engine._positions[i]}")
