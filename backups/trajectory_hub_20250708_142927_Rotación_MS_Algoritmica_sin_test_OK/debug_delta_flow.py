#!/usr/bin/env python3
"""Debug profundo del flujo de deltas para MacroRotation"""

import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine

print("🔍 DEBUG PROFUNDO: Flujo de Deltas")
print("=" * 60)

# Crear engine
engine = EnhancedTrajectoryEngine()

# Crear macro simple
macro_name = engine.create_macro("test", source_count=2)
print(f"✅ Macro creado: {macro_name}")

# Establecer posiciones
engine._positions[0] = np.array([2.0, 0.0, 0.0])
engine._positions[1] = np.array([-2.0, 0.0, 0.0])

print("\n📍 Posiciones iniciales:")
print(f"  F0: {engine._positions[0]}")
print(f"  F1: {engine._positions[1]}")

# Aplicar rotación
success = engine.set_macro_rotation(macro_name, speed_y=1.0)
print(f"\n🔄 Rotación aplicada: {success}")

# Debug: Verificar componentes
print("\n🔍 Verificando componentes:")
for sid in [0, 1]:
    if sid in engine.motion_states:
        motion = engine.motion_states[sid]
        print(f"\n  Fuente {sid}:")
        print(f"    motion_states existe: ✅")
        
        if 'macro_rotation' in motion.active_components:
            rot = motion.active_components['macro_rotation']
            print(f"    macro_rotation existe: ✅")
            print(f"    enabled: {rot.enabled}")
            print(f"    speed_y: {rot.speed_y}")
            print(f"    center: {rot.center}")
            
            # Probar calculate_delta directamente
            print(f"\n    🧪 Probando calculate_delta:")
            state = motion
            delta = rot.calculate_delta(state, 0.0, 0.016)
            print(f"    Delta calculado: {delta.position if hasattr(delta, 'position') else 'No position'}")
            
            # Probar update_with_deltas
            print(f"\n    🧪 Probando update_with_deltas:")
            if hasattr(motion, 'update_with_deltas'):
                deltas = motion.update_with_deltas(0.0, 0.016)
                print(f"    Deltas retornados: {len(deltas) if deltas else 0}")
                if deltas:
                    for i, d in enumerate(deltas):
                        print(f"      Delta {i}: {d.position if hasattr(d, 'position') else 'No position'}")
            else:
                print("    ❌ update_with_deltas no existe")
        else:
            print(f"    macro_rotation existe: ❌")
    else:
        print(f"\n  Fuente {sid}: ❌ No existe en motion_states")

# Simular UN solo frame con debug
print("\n⏱️ Simulando UN frame con debug...")

# Guardar posiciones antes
pos_before = [engine._positions[i].copy() for i in range(2)]

# Verificar dt
print(f"\n  dt = {1.0 / engine.fps if hasattr(engine, 'fps') else 'desconocido'}")

# Un update
print("\n  Ejecutando engine.update()...")
engine.update()

# Comparar posiciones
print("\n📊 Resultado:")
for i in range(2):
    before = pos_before[i]
    after = engine._positions[i]
    diff = after - before
    print(f"  F{i}: Antes={before} → Después={after}")
    print(f"       Cambio: {diff} (magnitud: {np.linalg.norm(diff):.6f})")

# Debug adicional del método update
print("\n🔍 Debug del método update:")
print(f"  ¿Tiene motion_states? {hasattr(engine, 'motion_states')}")
print(f"  ¿Tiene _time? {hasattr(engine, '_time')}")
print(f"  ¿Tiene dt? {hasattr(engine, 'dt')}")

# Intentar llamar directamente al procesamiento de deltas
if hasattr(engine, 'motion_states'):
    print("\n🧪 Procesando deltas manualmente:")
    for sid, motion in engine.motion_states.items():
        if sid < 2:  # Solo las primeras 2 fuentes
            if hasattr(motion, 'update_with_deltas'):
                deltas = motion.update_with_deltas(engine._time if hasattr(engine, '_time') else 0, 0.016)
                if deltas:
                    print(f"  Fuente {sid}: {len(deltas)} deltas")
                    for delta in deltas:
                        if hasattr(delta, 'position') and delta.position is not None:
                            print(f"    Aplicando delta: {delta.position}")
                            engine._positions[sid] += delta.position
                else:
                    print(f"  Fuente {sid}: Sin deltas")

print("\n📍 Posiciones después del procesamiento manual:")
for i in range(2):
    print(f"  F{i}: {engine._positions[i]}")
