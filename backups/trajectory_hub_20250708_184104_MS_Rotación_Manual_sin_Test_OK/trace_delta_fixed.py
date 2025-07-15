# === trace_delta_fixed.py ===
# 🔍 Rastrear transformación de deltas - CORREGIDO
# ⚡ Debug profundo del flujo de rotación

import sys
import os
import numpy as np
import math
import time

# Añadir la ruta del proyecto al PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def trace_delta_flow():
    """Rastrea el flujo completo del delta desde calculate_delta hasta las posiciones"""
    print("🔍 RASTREANDO FLUJO DE DELTAS")
    print("=" * 60)
    
    from trajectory_hub.core import EnhancedTrajectoryEngine
    
    # Crear engine simple - CORREGIDO: max_sources en lugar de n_sources
    print("\n1️⃣ Creando engine...")
    engine = EnhancedTrajectoryEngine(
        max_sources=50,
        fps=60,
        enable_modulator=False
    )
    
    # Crear fuentes en posiciones específicas
    print("\n2️⃣ Creando fuentes...")
    source_ids = []
    positions = [[3, 0, 0], [0, 3, 0], [-3, 0, 0], [0, -3, 0]]
    
    for i, pos in enumerate(positions):
        motion = engine.create_source(f"test_{i}")
        sid = i  # El ID es el índice
        engine._positions[sid] = np.array(pos, dtype=np.float32)
        source_ids.append(sid)
        print(f"   Fuente {sid}: {pos}")
    
    # Crear macro
    print("\n3️⃣ Creando macro...")
    macro_name = "test_macro"
    engine.create_macro(macro_name, len(source_ids))  # Usa count, no lista de IDs
    
    # Configurar rotación manual
    print("\n4️⃣ Configurando rotación manual...")
    engine.set_manual_macro_rotation(
        macro_name,
        yaw=math.pi/2,    # 90 grados
        pitch=0,
        roll=0,
        interpolation_speed=0.1
    )
    
    # Obtener el componente de rotación
    print("\n5️⃣ Obteniendo componente de rotación...")
    component = None
    macro = engine._macros.get(macro_name)
    if not macro:
        print("❌ No se encontró el macro")
        return
        
    # Buscar en las fuentes del macro
    for sid in macro.source_ids:
        if sid in engine.motion_states:
            motion = engine.motion_states[sid]
            if hasattr(motion, 'active_components') and 'manual_macro_rotation' in motion.active_components:
                component = motion.active_components['manual_macro_rotation']
                break
    
    if not component:
        print("❌ No se encontró componente de rotación")
        print(f"   Motion states disponibles: {list(engine.motion_states.keys())}")
        if engine.motion_states:
            first_motion = list(engine.motion_states.values())[0]
            print(f"   Active components en primera motion: {list(first_motion.active_components.keys()) if hasattr(first_motion, 'active_components') else 'No tiene'}")
        return
    
    print(f"✅ Componente encontrado: {type(component).__name__}")
    
    # Verificar el estado del componente
    print(f"   Enabled: {component.enabled}")
    print(f"   Target yaw: {component.target_yaw}")
    print(f"   Current yaw: {component.current_yaw}")
    print(f"   Center: {component.center}")
    
    # Trace manual del calculate_delta
    print("\n6️⃣ TRACE MANUAL DE calculate_delta:")
    print("-" * 40)
    
    # Probar calculate_delta directamente
    test_state = engine.motion_states[macro.source_ids[0]]
    test_delta = component.calculate_delta(test_state, 0.0, 0.016)
    
    if test_delta:
        print(f"✅ Delta directo: {test_delta.position}")
    else:
        print("❌ calculate_delta retornó None")
    
    # Ejecutar un update
    print("\n7️⃣ EJECUTANDO engine.update():")
    print("-" * 40)
    
    # Guardar posiciones antes
    positions_before = {}
    for sid in macro.source_ids:
        positions_before[sid] = engine._positions[sid].copy()
        print(f"   Antes - Fuente {sid}: {positions_before[sid]}")
    
    # Update
    engine.update()
    
    # Verificar posiciones después
    print("\n8️⃣ POSICIONES DESPUÉS:")
    for sid in macro.source_ids:
        pos_after = engine._positions[sid]
        diff = pos_after - positions_before[sid]
        print(f"   Fuente {sid}: {pos_after} (cambio: {diff})")
    
    # Diagnóstico adicional
    print("\n🔍 DIAGNÓSTICO ADICIONAL:")
    print("-" * 40)
    
    # Verificar si el método update existe en motion
    if macro.source_ids:
        motion = engine.motion_states[macro.source_ids[0]]
        print(f"¿motion tiene update?: {hasattr(motion, 'update')}")
        if hasattr(motion, 'update'):
            print("   Llamando motion.update() directamente...")
            motion.update(0.1, 0.016)
            
            # Ver si algo cambió
            test_delta2 = component.calculate_delta(test_state, 0.1, 0.016)
            if test_delta2:
                print(f"   Delta después de update: {test_delta2.position}")

if __name__ == "__main__":
    trace_delta_flow()