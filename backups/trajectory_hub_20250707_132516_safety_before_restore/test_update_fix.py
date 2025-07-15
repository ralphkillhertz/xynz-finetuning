#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
import numpy as np

print("🧪 TEST UPDATE FIX")

# Crear engine con sistema de deltas (parámetros correctos)
engine = EnhancedTrajectoryEngine(max_sources=4, fps=60)
engine.use_delta_system = True

# Crear macro
macro_id = engine.create_macro("test", source_count=2, formation="line", spacing=4.0)

# Configurar concentración
if hasattr(engine, 'set_macro_concentration'):
    engine.set_macro_concentration(macro_id, 0.5)
    print("✅ Concentración configurada")

# Posiciones iniciales
print(f"\nPosiciones iniciales:")
print(f"  Fuente 0: {engine._positions[0]}")
print(f"  Fuente 1: {engine._positions[1]}")

# Llamar update con dt
print("\n🔄 Llamando engine.update(0.016)...")
try:
    result = engine.update(0.016)
    print("✅ update() ejecutado")
except Exception as e:
    print(f"❌ Error en update: {e}")
    # Intentar sin parámetros
    print("\n🔄 Intentando engine.update() sin parámetros...")
    result = engine.update()

# Verificar movimiento
print(f"\nPosiciones después de update:")
print(f"  Fuente 0: {engine._positions[0]}")
print(f"  Fuente 1: {engine._positions[1]}")

# Calcular movimiento
movement = np.linalg.norm(engine._positions[0] - np.array([-2., 0., 0.]))
if movement > 0.001:
    print(f"\n✅ ¡FUNCIONA! Movimiento detectado: {movement:.4f}")
else:
    print(f"\n❌ Sin movimiento: {movement:.6f}")
    
    # Debug adicional
    if hasattr(engine, '_source_motions') and 0 in engine._source_motions:
        motion = engine._source_motions[0]
        print(f"\n🔍 Debug SourceMotion:")
        print(f"  motion_components: {hasattr(motion, 'motion_components')}")
        print(f"  use_delta_system: {getattr(motion, 'use_delta_system', False)}")
        if hasattr(motion, 'motion_components'):
            print(f"  Componentes: {list(motion.motion_components.keys())}")
