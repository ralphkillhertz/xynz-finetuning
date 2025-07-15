#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
import numpy as np

print("🔍 DIAGNÓSTICO UPDATE FLOW\n")

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=4, fps=60)
print(f"✅ Engine creado")
print(f"   use_delta_system: {getattr(engine, 'use_delta_system', 'NO EXISTE')}")
print(f"   _source_motions: {hasattr(engine, '_source_motions')}")

# Activar sistema de deltas
engine.use_delta_system = True
print(f"\n✅ Sistema de deltas activado")

# Crear macro
macro_id = engine.create_macro("test", source_count=2, formation="line", spacing=4.0)
print(f"\n✅ Macro creado: {macro_id}")

# Configurar concentración
engine.set_macro_concentration(macro_id, 0.5)
print(f"✅ Concentración configurada")

# Verificar SourceMotion
if hasattr(engine, '_source_motions') and 0 in engine._source_motions:
    motion = engine._source_motions[0]
    print(f"\n🔍 SourceMotion[0]:")
    print(f"   use_delta_system: {getattr(motion, 'use_delta_system', 'NO EXISTE')}")
    print(f"   motion_components: {hasattr(motion, 'motion_components')}")
    if hasattr(motion, 'motion_components'):
        print(f"   Componentes: {list(motion.motion_components.keys())}")

# Debug del update
print(f"\n🔄 Ejecutando update con debug...")

# Parchear temporalmente para debug
original_update = engine.update
def debug_update(dt=None):
    print(f"   -> update() llamado con dt={dt}")
    print(f"   -> use_delta_system={getattr(engine, 'use_delta_system', False)}")
    print(f"   -> _time={getattr(engine, '_time', 'NO EXISTE')}")
    
    # Llamar original
    result = original_update(dt)
    
    # Verificar si se llamó a motion.update
    if hasattr(engine, '_source_motions'):
        for sid, motion in engine._source_motions.items():
            if sid == 0:  # Solo debug primera fuente
                print(f"   -> SourceMotion[{sid}] position: {motion.state.position}")
    
    return result

engine.update = debug_update

# Llamar update
result = engine.update(0.016)

print(f"\n📊 Resultado:")
print(f"   Posición fuente 0: {engine._positions[0]}")
print(f"   Movimiento: {np.linalg.norm(engine._positions[0] - np.array([-4., 0., 0.]))}")
