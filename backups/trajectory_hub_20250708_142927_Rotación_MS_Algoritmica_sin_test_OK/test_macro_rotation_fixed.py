#!/usr/bin/env python3
"""Test de MacroRotation arreglada"""

import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine

print("🧪 Test MacroRotation Arreglada")

try:
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)
    print("✅ Engine creado")

    # Crear 4 fuentes en cuadrado
    positions = [[2,0,0], [-2,0,0], [0,2,0], [0,-2,0]]
    for i, pos in enumerate(positions):
        engine.create_source(position=pos)
        
    # Crear macro
    engine.create_macro("rot_test", [0,1,2,3])
    print("✅ Macro creado")

    # Estado inicial
    print("\n📍 Inicial:")
    for i in range(4):
        p = engine._positions[i]
        print(f"  F{i}: [{p[0]:5.2f}, {p[1]:5.2f}, {p[2]:5.2f}]")

    # Aplicar rotación
    print("\n🔄 Aplicando rotación Y=1.0 rad/s...")
    success = engine.set_macro_rotation("rot_test", speed_y=1.0)
    print(f"   Resultado: {success}")

    # Verificar que se configuró
    if hasattr(engine, 'motion_states'):
        rot_count = 0
        for sid in range(4):
            if sid in engine.motion_states:
                motion = engine.motion_states[sid]
                if 'macro_rotation' in motion.active_components:
                    rot = motion.active_components['macro_rotation']
                    if rot.enabled:
                        rot_count += 1
        print(f"   Componentes activos: {rot_count}/4")

    # Simular 1 segundo
    print("\n⏱️ Simulando...")
    for i in range(60):
        engine.update()
        if i % 20 == 0:
            print(f"  {i}/60 frames...")

    # Estado final
    print("\n📍 Final:")
    moved = False
    for i in range(4):
        p = engine._positions[i]
        dist = np.linalg.norm(p - positions[i])
        print(f"  F{i}: [{p[0]:5.2f}, {p[1]:5.2f}, {p[2]:5.2f}] (movió {dist:.3f})")
        if dist > 0.1:
            moved = True

    print(f"\n{'✅' if moved else '❌'} {'Rotación funciona!' if moved else 'Sin movimiento'}")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
