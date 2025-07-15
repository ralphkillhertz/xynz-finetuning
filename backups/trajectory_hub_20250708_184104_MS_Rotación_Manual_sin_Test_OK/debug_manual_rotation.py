# === debug_manual_rotation.py ===
# 🔍 Debug para encontrar por qué no funciona la rotación manual

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np
import math

print("🔍 DEBUG DE ROTACIÓN MANUAL")
print("=" * 60)

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=5, fps=60, enable_modulator=False)
print("✅ Engine creado")

# Crear macro
macro_name = engine.create_macro("test", source_count=2)
macro = engine._macros[macro_name]
source_ids = list(macro.source_ids)
print(f"✅ Macro creado con fuentes: {source_ids}")

# Establecer posiciones manualmente
print("\n📍 Estableciendo posiciones manuales:")
engine._positions[source_ids[0]] = np.array([5.0, 0.0, 0.0])
engine._positions[source_ids[1]] = np.array([0.0, 5.0, 0.0])

for sid in source_ids:
    print(f"   Fuente {sid}: {engine._positions[sid]}")

# Configurar rotación manual
print("\n🔧 Configurando rotación manual...")
success = engine.set_manual_macro_rotation(
    macro_name,
    yaw=math.pi/2,  # 90 grados
    interpolation_speed=0.5  # Rápido para test
)

if not success:
    print("❌ Error configurando rotación")
    exit(1)

print("✅ Rotación configurada")

# Verificar que el componente existe
print("\n🔍 Verificando componentes:")
for sid in source_ids:
    motion = engine.motion_states[sid]
    print(f"\nFuente {sid}:")
    print(f"  - Componentes activos: {list(motion.active_components.keys())}")
    
    if 'manual_macro_rotation' in motion.active_components:
        rotation = motion.active_components['manual_macro_rotation']
        print(f"  - Rotación manual:")
        print(f"    - enabled: {rotation.enabled}")
        print(f"    - target_yaw: {rotation.target_yaw}")
        print(f"    - current_yaw: {rotation.current_yaw}")
        print(f"    - interpolation_speed: {rotation.interpolation_speed}")
        print(f"    - center: {rotation.center}")
        
        # Probar calculate_delta directamente
        print("\n  🧪 Probando calculate_delta directamente:")
        state = motion.state
        print(f"    - state.position: {state.position}")
        
        # Llamar calculate_delta
        delta = rotation.calculate_delta(state, 1.0, 0.1)
        
        if delta:
            print(f"    - Delta retornado: {delta}")
            print(f"    - Delta.position: {delta.position}")
        else:
            print("    - Delta es None")

# Ejecutar algunos updates
print("\n🔄 Ejecutando updates...")
for i in range(5):
    print(f"\nUpdate {i}:")
    
    # Posiciones antes
    pos_before = [engine._positions[sid].copy() for sid in source_ids]
    
    # Update
    engine.update()
    
    # Posiciones después
    for j, sid in enumerate(source_ids):
        pos_after = engine._positions[sid]
        diff = pos_after - pos_before[j]
        print(f"  Fuente {sid}: {pos_after} (cambio: {diff})")
        
        # Ver el current_yaw
        if sid in engine.motion_states:
            motion = engine.motion_states[sid]
            if 'manual_macro_rotation' in motion.active_components:
                rotation = motion.active_components['manual_macro_rotation']
                print(f"    current_yaw: {rotation.current_yaw:.3f}")

# Debug del método update del engine
print("\n🔍 Verificando engine.update():")
print(f"  - motion_states tiene {len(engine.motion_states)} elementos")

# Verificar si update_with_deltas se está llamando
sid = source_ids[0]
motion = engine.motion_states[sid]
print(f"\n🧪 Llamando update_with_deltas manualmente:")
deltas = motion.update_with_deltas(2.0, 0.1)
print(f"  - Deltas retornados: {deltas}")
if deltas:
    for i, d in enumerate(deltas):
        print(f"    - Delta {i}: {d}")
        if hasattr(d, 'position'):
            print(f"      position: {d.position}")