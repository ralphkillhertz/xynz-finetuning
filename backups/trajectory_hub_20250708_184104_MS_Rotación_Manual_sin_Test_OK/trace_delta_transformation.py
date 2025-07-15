# === trace_delta_transformation.py ===
# 🔍 Rastrear transformación de deltas
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
        n_sources=5,
        update_rate=60,
        enable_modulator=False
    )
    
    # Crear fuentes en posiciones específicas
    print("\n2️⃣ Creando fuentes...")
    source_ids = []
    positions = [[3, 0, 0], [0, 3, 0], [-3, 0, 0], [0, -3, 0]]
    
    for i, pos in enumerate(positions):
        sid = engine.create_source(f"test_{i}")
        engine._positions[sid] = np.array(pos, dtype=np.float32)
        source_ids.append(sid)
        print(f"   Fuente {sid}: {pos}")
    
    # Crear macro
    print("\n3️⃣ Creando macro...")
    macro_name = "test_macro"
    engine.create_macro(macro_name, source_ids)
    
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
    for sid in source_ids:
        if sid in engine.motion_states:
            motion = engine.motion_states[sid]
            if hasattr(motion, 'active_components') and 'manual_macro_rotation' in motion.active_components:
                component = motion.active_components['manual_macro_rotation']
                break
    
    if not component:
        print("❌ No se encontró componente de rotación")
        return
    
    print(f"✅ Componente encontrado: {component}")
    
    # Trace manual del calculate_delta
    print("\n6️⃣ TRACE MANUAL DE calculate_delta:")
    print("-" * 40)
    
    # Interceptar el método para debug
    original_calculate_delta = component.calculate_delta
    
    def traced_calculate_delta(state, current_time, dt):
        print(f"\n📍 calculate_delta llamado:")
        print(f"   State position: {state.position}")
        print(f"   Current time: {current_time}")
        print(f"   dt: {dt}")
        
        # Calcular manualmente para comparar
        current_position = np.array(state.position)
        relative_pos = current_position - component.center
        distance_xy = np.sqrt(relative_pos[0]**2 + relative_pos[1]**2)
        
        print(f"   Relative position: {relative_pos}")
        print(f"   Distance XY: {distance_xy}")
        
        if distance_xy < 0.001:
            print("   ⚠️ Muy cerca del centro!")
        
        # Llamar al método original
        result = original_calculate_delta(state, current_time, dt)
        
        if result:
            print(f"   ✅ Delta calculado: {result.position}")
        else:
            print("   ❌ Delta es None")
        
        return result
    
    # Reemplazar temporalmente
    component.calculate_delta = traced_calculate_delta
    
    # Obtener estado inicial
    print("\n7️⃣ Posiciones iniciales:")
    for sid in source_ids:
        pos = engine._positions[sid]
        print(f"   Fuente {sid}: {pos}")
    
    # Interceptar update_with_deltas
    print("\n8️⃣ INTERCEPTANDO update_with_deltas:")
    print("-" * 40)
    
    if sid in engine.motion_states:
        motion = engine.motion_states[sid]
        original_update_with_deltas = motion.update_with_deltas
        
        def traced_update_with_deltas(current_time, dt):
            print(f"\n📍 update_with_deltas llamado:")
            print(f"   Current time: {current_time}")
            print(f"   dt: {dt}")
            
            result = original_update_with_deltas(current_time, dt)
            
            if isinstance(result, list):
                print(f"   ✅ Retornó lista con {len(result)} deltas")
                for i, delta in enumerate(result):
                    if delta:
                        print(f"      Delta {i}: {delta.position}")
            else:
                print(f"   ⚠️ Retornó: {type(result)}")
            
            return result
        
        motion.update_with_deltas = traced_update_with_deltas
    
    # Ejecutar un update
    print("\n9️⃣ EJECUTANDO engine.update():")
    print("-" * 40)
    
    # Interceptar el método step para ver qué pasa con los deltas
    original_step = engine.step
    
    def traced_step():
        print("\n📍 step() llamado")
        
        # Guardar posiciones antes
        positions_before = {}
        for sid in source_ids:
            positions_before[sid] = engine._positions[sid].copy()
        
        # Llamar al step original
        result = original_step()
        
        # Comparar posiciones después
        print("\n📊 Cambios en posiciones:")
        for sid in source_ids:
            before = positions_before[sid]
            after = engine._positions[sid]
            diff = after - before
            if np.any(diff != 0):
                print(f"   Fuente {sid}: {before} → {after} (cambio: {diff})")
            else:
                print(f"   Fuente {sid}: Sin cambios")
        
        return result
    
    engine.step = traced_step
    
    # Ejecutar el update
    engine.update()
    
    # Verificar estado final
    print("\n🎯 ESTADO FINAL:")
    print("-" * 40)
    for sid in source_ids:
        pos = engine._positions[sid]
        print(f"   Fuente {sid}: {pos}")
    
    # Buscar el problema
    print("\n🔍 ANÁLISIS:")
    print("-" * 40)
    print("Si los deltas se calculan correctamente pero las posiciones no cambian,")
    print("el problema está en cómo engine.update() procesa los deltas.")
    print("\nPosibles causas:")
    print("1. update_with_deltas no retorna los deltas correctamente")
    print("2. engine.update() no procesa los deltas de ManualMacroRotation")
    print("3. Hay otro código que sobrescribe las posiciones")

if __name__ == "__main__":
    trace_delta_flow()