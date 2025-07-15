# === trace_delta_correct.py ===
# 🔍 Rastrear transformación de deltas - NOMBRE CORRECTO
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
    
    # Crear macro
    print("\n2️⃣ Creando macro...")
    base_name = "test_macro"
    engine.create_macro(base_name, 4, formation="square")
    
    # El nombre real del macro incluye un prefijo
    macro_name = list(engine._macros.keys())[0]  # Tomar el primer (y único) macro
    print(f"✅ Macro creado con nombre: '{macro_name}'")
    
    macro = engine._macros[macro_name]
    print(f"   IDs de fuentes: {macro.source_ids}")
    
    # Establecer posiciones específicas
    print("\n3️⃣ Estableciendo posiciones de test...")
    positions = [[3, 0, 0], [0, 3, 0], [-3, 0, 0], [0, -3, 0]]
    
    for i, (sid, pos) in enumerate(zip(macro.source_ids, positions)):
        engine._positions[sid] = np.array(pos, dtype=np.float32)
        print(f"   Fuente {sid}: {pos}")
    
    # Configurar rotación manual
    print("\n4️⃣ Configurando rotación manual...")
    engine.set_manual_macro_rotation(
        macro_name,  # Usar el nombre real
        yaw=math.pi/2,    # 90 grados
        pitch=0,
        roll=0,
        interpolation_speed=0.1
    )
    
    # Buscar componente
    print("\n5️⃣ Verificando componente de rotación...")
    component = None
    test_sid = None
    
    for sid in macro.source_ids:
        if sid in engine.motion_states:
            motion = engine.motion_states[sid]
            if hasattr(motion, 'active_components') and 'manual_macro_rotation' in motion.active_components:
                component = motion.active_components['manual_macro_rotation']
                test_sid = sid
                break
    
    if not component:
        print("❌ No se encontró componente")
        # Debug detallado
        if macro.source_ids:
            sid = macro.source_ids[0]
            if sid in engine.motion_states:
                motion = engine.motion_states[sid]
                print(f"   Motion type: {type(motion).__name__}")
                if hasattr(motion, 'active_components'):
                    print(f"   Componentes: {list(motion.active_components.keys())}")
        return
    
    print(f"✅ Componente encontrado")
    print(f"   Enabled: {component.enabled}")
    print(f"   Target yaw: {math.degrees(component.target_yaw):.1f}°")
    print(f"   Speed: {component.interpolation_speed}")
    
    # Test calculate_delta
    print("\n6️⃣ TEST calculate_delta:")
    print("-" * 40)
    
    # Sincronizar estado
    test_state = engine.motion_states[test_sid]
    test_state.position = engine._positions[test_sid].copy()
    print(f"   Posición: {test_state.position}")
    
    # Calcular delta
    delta = component.calculate_delta(test_state, 0.0, 0.016)
    
    if delta and delta.position is not None:
        print(f"   ✅ Delta: {delta.position}")
        print(f"   Magnitud: {np.linalg.norm(delta.position):.6f}")
    else:
        print("   ❌ Sin delta")
    
    # Posiciones antes
    print("\n7️⃣ ANTES del update:")
    pos_before = {}
    for sid in macro.source_ids:
        pos_before[sid] = engine._positions[sid].copy()
        print(f"   Fuente {sid}: {pos_before[sid]}")
    
    # Update
    print("\n8️⃣ Ejecutando engine.update()...")
    
    # Sincronizar todos los estados
    for sid in macro.source_ids:
        if sid in engine.motion_states:
            engine.motion_states[sid].position = engine._positions[sid].copy()
    
    engine.update()
    
    # Después
    print("\n9️⃣ DESPUÉS del update:")
    changed = False
    for sid in macro.source_ids:
        pos_after = engine._positions[sid]
        diff = np.linalg.norm(pos_after - pos_before[sid])
        
        if diff > 0.0001:
            print(f"   Fuente {sid}: {pos_after} ✅ ({diff:.6f})")
            changed = True
        else:
            print(f"   Fuente {sid}: {pos_after} ❌")
    
    # Análisis
    print("\n📊 RESULTADO:")
    print("=" * 60)
    
    if delta and np.any(delta.position != 0):
        print("✅ calculate_delta funciona")
    else:
        print("❌ calculate_delta falla")
    
    if changed:
        print("✅ engine.update() aplica cambios")
    else:
        print("❌ engine.update() NO aplica deltas")
        print("\n🔍 El problema está en engine.update()")
        print("   Los deltas se calculan pero no se aplican")

if __name__ == "__main__":
    trace_delta_flow()