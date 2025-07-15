# === trace_delta_final.py ===
# 🔍 Rastrear transformación de deltas - VERSIÓN FINAL
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
    
    # Crear engine simple
    print("\n1️⃣ Creando engine...")
    engine = EnhancedTrajectoryEngine(
        max_sources=50,
        fps=60,
        enable_modulator=False
    )
    
    # Crear fuentes con IDs numéricos
    print("\n2️⃣ Creando fuentes...")
    positions = [[3, 0, 0], [0, 3, 0], [-3, 0, 0], [0, -3, 0]]
    
    for i, pos in enumerate(positions):
        # create_source espera un ID numérico
        motion = engine.create_source(i)
        engine._positions[i] = np.array(pos, dtype=np.float32)
        print(f"   Fuente {i}: {pos}")
    
    # Crear macro
    print("\n3️⃣ Creando macro...")
    macro_name = "test_macro"
    engine.create_macro(macro_name, 4)  # 4 fuentes
    
    # Configurar rotación manual
    print("\n4️⃣ Configurando rotación manual...")
    engine.set_manual_macro_rotation(
        macro_name,
        yaw=math.pi/2,    # 90 grados
        pitch=0,
        roll=0,
        interpolation_speed=0.1
    )
    
    # Obtener el macro
    macro = engine._macros.get(macro_name)
    if not macro:
        print("❌ No se encontró el macro")
        return
    
    print(f"✅ Macro encontrado con {len(macro.source_ids)} fuentes")
    
    # Buscar componente de rotación
    print("\n5️⃣ Buscando componente de rotación...")
    component = None
    motion_with_component = None
    
    for sid in macro.source_ids:
        if sid in engine.motion_states:
            motion = engine.motion_states[sid]
            if hasattr(motion, 'active_components') and 'manual_macro_rotation' in motion.active_components:
                component = motion.active_components['manual_macro_rotation']
                motion_with_component = motion
                break
    
    if not component:
        print("❌ No se encontró componente de rotación")
        # Debug adicional
        if macro.source_ids and macro.source_ids[0] in engine.motion_states:
            motion = engine.motion_states[macro.source_ids[0]]
            print(f"   Tipo de motion: {type(motion).__name__}")
            if hasattr(motion, 'active_components'):
                print(f"   Active components: {list(motion.active_components.keys())}")
        return
    
    print(f"✅ Componente encontrado: {type(component).__name__}")
    print(f"   Enabled: {component.enabled}")
    print(f"   Target yaw: {component.target_yaw:.3f} rad ({math.degrees(component.target_yaw):.1f}°)")
    print(f"   Current yaw: {component.current_yaw:.3f}")
    print(f"   Center: {component.center}")
    
    # Test directo de calculate_delta
    print("\n6️⃣ TEST DIRECTO de calculate_delta:")
    print("-" * 40)
    
    test_state = engine.motion_states[macro.source_ids[0]]
    print(f"   Estado inicial: position={test_state.position}")
    
    # Llamar calculate_delta directamente
    delta = component.calculate_delta(test_state, 0.0, 0.016)
    
    if delta:
        print(f"   ✅ Delta calculado: {delta.position}")
        print(f"      Magnitud: {np.linalg.norm(delta.position):.6f}")
    else:
        print("   ❌ calculate_delta retornó None")
    
    # Guardar posiciones antes del update
    print("\n7️⃣ POSICIONES ANTES del update:")
    positions_before = {}
    for sid in macro.source_ids:
        positions_before[sid] = engine._positions[sid].copy()
        print(f"   Fuente {sid}: {positions_before[sid]}")
    
    # Ejecutar engine.update()
    print("\n8️⃣ Ejecutando engine.update()...")
    engine.update()
    
    # Verificar cambios
    print("\n9️⃣ POSICIONES DESPUÉS del update:")
    any_change = False
    for sid in macro.source_ids:
        pos_after = engine._positions[sid]
        diff = pos_after - positions_before[sid]
        magnitude = np.linalg.norm(diff)
        
        if magnitude > 0.0001:
            print(f"   Fuente {sid}: {pos_after} ✅ (cambió {magnitude:.6f})")
            any_change = True
        else:
            print(f"   Fuente {sid}: {pos_after} ❌ (sin cambios)")
    
    # Análisis final
    print("\n🔍 ANÁLISIS FINAL:")
    print("-" * 40)
    
    if delta and delta.position is not None and np.any(delta.position != 0):
        print("✅ calculate_delta funciona correctamente")
    else:
        print("❌ calculate_delta NO está generando deltas")
    
    if any_change:
        print("✅ engine.update() SÍ aplica cambios")
    else:
        print("❌ engine.update() NO aplica los deltas")
        
        # Debug adicional
        print("\n📍 Debug adicional:")
        print(f"   ¿motion tiene update?: {hasattr(motion_with_component, 'update')}")
        print(f"   ¿motion tiene update_with_deltas?: {hasattr(motion_with_component, 'update_with_deltas')}")
        
        # Verificar si engine.update llama a motion.update
        print("\n   Verificando el flujo de update...")
        if hasattr(engine, 'motion_states'):
            print(f"   Engine tiene {len(engine.motion_states)} motion states")

if __name__ == "__main__":
    trace_delta_flow()