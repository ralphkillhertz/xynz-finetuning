#!/usr/bin/env python3
"""
🧪 TEST RÁPIDO DE CONCENTRACIÓN
⚡ Verifica que los fixes funcionan
"""

import sys
import os
import numpy as np

# Importar módulos
try:
    from core.trajectory_engine import TrajectoryEngine
    print("✅ Usando TrajectoryEngine")
except:
    try:
        from core.spatial_engine import SpatialEngine as TrajectoryEngine
        print("✅ Usando SpatialEngine")
    except:
        from core.engine import SpatialEngine as TrajectoryEngine
        print("✅ Usando engine genérico")

print("=" * 50)
print("🧪 TEST DE CONCENTRACIÓN")
print("=" * 50)

# Crear engine
engine = TrajectoryEngine(num_sources=3)
engine.initialize()

# Estado inicial
print("\n📍 POSICIONES INICIALES:")
for i in range(3):
    pos = engine._positions[i] if hasattr(engine, '_positions') else engine.positions[i]
    print(f"  Fuente {i}: {pos}")

# Activar concentración
if 'concentration' in engine.modules:
    conc = engine.modules['concentration']
    conc.enabled = True
    conc.update_parameter('factor', 0.0)  # Máxima concentración
    print("\n✅ Concentración activada (factor=0.0)")
    
    # 10 updates
    print("\n⏳ Ejecutando 10 updates...")
    for _ in range(10):
        engine.update()
    
    # Verificar resultado
    print("\n📍 POSICIONES FINALES:")
    all_at_origin = True
    for i in range(3):
        pos = engine._positions[i] if hasattr(engine, '_positions') else engine.positions[i]
        dist = np.linalg.norm(pos)
        print(f"  Fuente {i}: {pos} (dist: {dist:.3f})")
        if dist > 0.01:
            all_at_origin = False
    
    if all_at_origin:
        print("\n✅ ¡CONCENTRACIÓN FUNCIONA PERFECTAMENTE!")
    else:
        print("\n❌ Concentración NO funciona completamente")
        
        # Debug adicional
        motion = engine._source_motions[0] if hasattr(engine, '_source_motions') else engine.source_motions[0]
        print(f"\nDEBUG:")
        print(f"  motion.state.position: {motion.state.position}")
        print(f"  _positions[0]: {engine._positions[0] if hasattr(engine, '_positions') else engine.positions[0]}")
        
        # Verificar componentes
        if hasattr(motion, 'components'):
            print(f"\n  Componentes activos:")
            for name, comp in motion.components.items():
                if hasattr(comp, 'enabled') and comp.enabled:
                    print(f"    - {name}: enabled")
else:
    print("\n❌ Módulo de concentración no encontrado")

print("\n" + "=" * 50)
print("Si no funciona, ejecuta en orden:")
print("1. python fix_engine_propagation.py")
print("2. python fix_modes_rotation.py")
print("3. Reinicia el controlador")
print("=" * 50)