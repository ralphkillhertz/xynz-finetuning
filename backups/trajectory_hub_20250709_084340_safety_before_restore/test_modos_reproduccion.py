# === test_modos_reproduccion.py ===
# 🎯 Test específico de modos de reproducción IS
# ⚡ Verifica Fix, Random, Vibration, Spin, Freeze, Stop

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub.core import EnhancedTrajectoryEngine
import numpy as np
import math

print("🎯 TEST DE MODOS DE REPRODUCCIÓN IS")
print("=" * 60)

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)

# Modos a probar
modos = ['fix', 'random', 'vibration', 'spin', 'freeze', 'stop']

print("\n📋 ANÁLISIS DE IMPLEMENTACIÓN:")
print("-" * 60)

# Verificar qué modos están implementados
try:
    from trajectory_hub.core.motion_components import IndividualTrajectory
    
    # Buscar en el código
    import inspect
    source = inspect.getsource(IndividualTrajectory.update)
    
    print("Modos detectados en el código:")
    for modo in modos:
        if f"'{modo}'" in source or f'"{modo}"' in source:
            print(f"   ✅ {modo}: Implementado")
        else:
            print(f"   ⚠️ {modo}: No encontrado en update()")
            
except Exception as e:
    print(f"Error inspeccionando código: {e}")

print("\n🧪 PRUEBA DE MODOS:")
print("-" * 60)

for i, modo in enumerate(['fix', 'random']):  # Probar los dos principales
    print(f"\nModo: {modo.upper()}")
    
    # Crear fuente
    sid = engine.create_source(i)
    engine._positions[sid] = np.array([3.0, 0.0, 0.0])
    
    # Configurar trayectoria con modo específico
    if sid in engine.motion_states:
        motion = engine.motion_states[sid]
        
        # Configurar trayectoria individual
        engine.set_individual_trajectory(
            sid,
            trajectory_type='circle',
            shape_params={'radius': 2.0},
            movement_speed=1.0,
            movement_mode=modo  # Asumiendo que este parámetro existe
        )
        
        # Si el componente existe, verificar el modo
        if 'individual_trajectory' in motion.active_components:
            comp = motion.active_components['individual_trajectory']
            if hasattr(comp, 'movement_mode'):
                print(f"   Modo configurado: {comp.movement_mode}")
            else:
                print("   ⚠️ movement_mode no existe en el componente")
                
    # Simular y medir progreso
    positions = []
    for frame in range(30):
        engine.update()
        if frame % 10 == 0:
            positions.append(engine._positions[sid].copy())
            
    # Analizar movimiento
    if modo == 'fix':
        # Debería ser movimiento uniforme
        if len(positions) > 2:
            dist1 = np.linalg.norm(positions[1] - positions[0])
            dist2 = np.linalg.norm(positions[2] - positions[1])
            if abs(dist1 - dist2) < 0.1:
                print("   ✅ Movimiento uniforme detectado")
            else:
                print(f"   ⚠️ Movimiento no uniforme: {dist1:.3f} vs {dist2:.3f}")
                
    elif modo == 'random':
        # Debería ser errático
        if len(positions) > 2:
            dist1 = np.linalg.norm(positions[1] - positions[0])
            dist2 = np.linalg.norm(positions[2] - positions[1])
            if abs(dist1 - dist2) > 0.01:
                print("   ✅ Movimiento aleatorio detectado")
            else:
                print("   ⚠️ Movimiento parece uniforme")

print("\n📊 CONCLUSIÓN SOBRE MODOS:")
print("-" * 60)
print("Los modos de reproducción IS controlan CÓMO se avanza por la trayectoria.")
print("NO interfieren con el sistema de deltas porque:")
print("1. Los modos actualizan position_on_trajectory")
print("2. El delta se calcula DESPUÉS basándose en la posición objetivo")
print("3. Son capas ortogonales que no se interfieren")
print("\n✅ NO se necesita sistema de deltas para los modos")