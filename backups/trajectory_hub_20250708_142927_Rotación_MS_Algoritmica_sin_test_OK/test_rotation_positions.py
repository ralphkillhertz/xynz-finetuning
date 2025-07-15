#!/usr/bin/env python3
"""Test con verificación de posiciones"""

import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine

print("🧪 Test MacroRotation con Debug de Posiciones")
print("=" * 50)

# Crear engine
engine = EnhancedTrajectoryEngine()

# Crear macro
macro_name = engine.create_macro(
    name="rot_test",
    source_count=4,
    formation="square",
    spacing=4.0
)
print(f"✅ Macro creado: {macro_name}")

# Verificar macro
macro = engine._macros[macro_name]
source_ids = list(macro.source_ids)
print(f"   Source IDs: {source_ids}")

# IMPORTANTE: Aplicar la formación
print("\n🔧 Aplicando formación square...")
if hasattr(engine, 'apply_behavior'):
    engine.apply_behavior(macro_name, 'rigid')  # Comportamiento rígido
if hasattr(engine, 'set_macro_formation'):
    engine.set_macro_formation(macro_name, 'square', spacing=4.0)

# Alternativa: establecer posiciones manualmente
print("\n📍 Estableciendo posiciones manualmente...")
positions = [
    [4.0, 0.0, 0.0],   # Derecha
    [0.0, 4.0, 0.0],   # Arriba
    [-4.0, 0.0, 0.0],  # Izquierda
    [0.0, -4.0, 0.0]   # Abajo
]

for i, sid in enumerate(source_ids[:4]):
    engine._positions[sid] = np.array(positions[i], dtype=np.float32)
    pos = engine._positions[sid]
    print(f"  Fuente {sid}: [{pos[0]:6.2f}, {pos[1]:6.2f}, {pos[2]:6.2f}]")

# Aplicar rotación
print("\n🔄 Aplicando rotación Y=1.0 rad/s...")
success = engine.set_macro_rotation(macro_name, speed_y=1.0)
print(f"   Resultado: {success}")

# Verificar componentes
if success:
    print("\n🔍 Verificando componentes:")
    for sid in source_ids[:4]:
        if sid in engine.motion_states:
            motion = engine.motion_states[sid]
            if 'macro_rotation' in motion.active_components:
                rot = motion.active_components['macro_rotation']
                print(f"  Fuente {sid}: enabled={rot.enabled}, speed_y={rot.speed_y}")

# Simular
print("\n⏱️ Simulando 30 frames...")
initial_pos = {sid: engine._positions[sid].copy() for sid in source_ids[:4]}

for frame in range(30):
    engine.update()
    
    if frame == 29:  # Último frame
        print("\n📊 Posiciones finales:")
        for sid in source_ids[:4]:
            initial = initial_pos[sid]
            final = engine._positions[sid]
            dist = np.linalg.norm(final - initial)
            
            print(f"  Fuente {sid}:")
            print(f"    Inicial: [{initial[0]:6.2f}, {initial[1]:6.2f}, {initial[2]:6.2f}]")
            print(f"    Final:   [{final[0]:6.2f}, {final[1]:6.2f}, {final[2]:6.2f}]")
            print(f"    Distancia: {dist:.3f}")

# Verificar movimiento
moved = any(np.linalg.norm(engine._positions[sid] - initial_pos[sid]) > 0.1 
            for sid in source_ids[:4])

print(f"\n{'✅ ÉXITO' if moved else '❌ FALLO'}: {'Rotación funciona' if moved else 'Sin movimiento'}")
