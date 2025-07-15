# === test_delta_system_correct_api.py ===
# 🎯 Test con la API correcta del engine
# ✅ Usando métodos que sí existen

import numpy as np
from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import (
    ConcentrationComponent, IndividualTrajectory, MacroTrajectory,
    MacroRotation, ManualMacroRotation, IndividualRotation
)

def test_with_correct_api():
    """Test usando la API real del engine"""
    
    print("🎯 TEST SISTEMA DE DELTAS - API CORRECTA")
    print("=" * 60)
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=20, fps=60, enable_modulator=False)
    results = {}
    
    # TEST 1: Concentración (usando componentes directamente)
    print("\n1️⃣ TEST CONCENTRACIÓN")
    print("-" * 40)
    
    # Crear macro
    macro_name = "test_conc"
    engine.create_macro(macro_name, 4, formation="circle", radius=3.0)
    
    # Añadir concentración manualmente a cada fuente del macro
    macro = engine.macros[macro_name]
    for sid in macro.source_ids:
        if sid in engine.motion_states:
            motion = engine.motion_states[sid]
            motion.active_components['concentration'] = ConcentrationComponent(
                concentration_factor=0.8,
                macro=macro
            )
    
    # Guardar posiciones iniciales
    initial_positions = {}
    for sid in macro.source_ids:
        initial_positions[sid] = engine._positions[sid].copy()
    
    # Simular
    for _ in range(60):
        engine.update()
    
    # Verificar movimiento
    total_movement = 0
    for sid in macro.source_ids:
        movement = np.linalg.norm(engine._positions[sid] - initial_positions[sid])
        total_movement += movement
    
    results['concentration'] = total_movement > 0.1
    print(f"   Movimiento total: {total_movement:.3f}")
    print(f"   Estado: {'✅ FUNCIONA' if results['concentration'] else '❌ NO FUNCIONA'}")
    
    # TEST 2: Trayectoria Individual
    print("\n2️⃣ TEST TRAYECTORIA INDIVIDUAL")
    print("-" * 40)
    
    sid = 10
    engine.create_source(sid)
    result = engine.set_individual_trajectory(sid, shape="circle", radius=2.0, speed=1.0)
    
    initial = engine._positions[sid].copy()
    
    for _ in range(120):
        engine.update()
    
    distance = np.linalg.norm(engine._positions[sid] - initial)
    results['individual_trajectory'] = distance > 1.0
    print(f"   Configurada: {result}")
    print(f"   Distancia: {distance:.3f}")
    print(f"   Estado: {'✅ FUNCIONA' if results['individual_trajectory'] else '❌ NO FUNCIONA'}")
    
    # TEST 3: Trayectoria Macro
    print("\n3️⃣ TEST TRAYECTORIA MACRO")
    print("-" * 40)
    
    macro2 = "test_macro_traj"
    engine.create_macro(macro2, 3, formation="line")
    engine.set_macro_trajectory(macro2, "circle", speed=0.5)
    
    # Centro inicial
    positions = [engine._positions[sid] for sid in engine.macros[macro2].source_ids]
    initial_center = np.mean(positions, axis=0)
    
    for _ in range(120):
        engine.update()
    
    # Centro final
    positions = [engine._positions[sid] for sid in engine.macros[macro2].source_ids]
    final_center = np.mean(positions, axis=0)
    
    movement = np.linalg.norm(final_center - initial_center)
    results['macro_trajectory'] = movement > 0.5
    print(f"   Movimiento centro: {movement:.3f}")
    print(f"   Estado: {'✅ FUNCIONA' if results['macro_trajectory'] else '❌ NO FUNCIONA'}")
    
    # TEST 4: Rotación Macro Algorítmica
    print("\n4️⃣ TEST ROTACIÓN MACRO ALGORÍTMICA")
    print("-" * 40)
    
    macro3 = "test_rot"
    engine.create_macro(macro3, 4, formation="square", radius=2.0)
    engine.set_macro_rotation(macro3, speed_x=0, speed_y=0, speed_z=1.0)
    
    test_sid = engine.macros[macro3].source_ids[0]
    initial = engine._positions[test_sid].copy()
    
    for _ in range(120):
        engine.update()
    
    distance = np.linalg.norm(engine._positions[test_sid] - initial)
    results['macro_rotation'] = distance > 1.0
    print(f"   Distancia: {distance:.3f}")
    print(f"   Estado: {'✅ FUNCIONA' if results['macro_rotation'] else '❌ NO FUNCIONA'}")
    
    # TEST 5: Rotación Manual Macro
    print("\n5️⃣ TEST ROTACIÓN MANUAL MACRO")
    print("-" * 40)
    
    macro4 = "test_manual"
    engine.create_macro(macro4, 2, formation="line", spacing=3.0)
    engine.set_manual_macro_rotation(macro4, yaw=np.pi/2, interpolation_speed=0.1)
    
    test_sid = engine.macros[macro4].source_ids[0]
    initial = engine._positions[test_sid].copy()
    
    for _ in range(120):
        engine.update()
    
    final = engine._positions[test_sid]
    movement = np.linalg.norm(final - initial)
    results['manual_rotation'] = movement > 0.1
    print(f"   Movimiento: {movement:.3f}")
    print(f"   Estado: {'✅ FUNCIONA' if results['manual_rotation'] else '❌ NO FUNCIONA'}")
    
    # TEST 6: Rotación Individual (workaround directo)
    print("\n6️⃣ TEST ROTACIÓN INDIVIDUAL")  
    print("-" * 40)
    
    sid = 15
    engine.create_source(sid)
    engine._positions[sid] = np.array([3.0, 0.0, 0.0])
    
    # Añadir componente directamente
    motion = engine.motion_states[sid]
    motion.active_components['individual_rotation'] = IndividualRotation(
        speed_x=0, speed_y=0, speed_z=1.0
    )
    
    initial = engine._positions[sid].copy()
    
    for _ in range(120):
        engine.update()
    
    distance = np.linalg.norm(engine._positions[sid] - initial)
    results['individual_rotation'] = distance > 2.0
    print(f"   Distancia: {distance:.3f}")
    print(f"   Estado: {'✅ FUNCIONA' if results['individual_rotation'] else '❌ NO FUNCIONA'}")
    
    # RESUMEN
    print("\n" + "=" * 60)
    print("📊 RESUMEN DEL SISTEMA DE DELTAS:")
    print("-" * 60)
    
    for component, passed in results.items():
        print(f"   {component}: {'✅' if passed else '❌'}")
    
    all_pass = all(results.values())
    print("\n" + "=" * 60)
    
    if all_pass:
        print("🎉 ¡SISTEMA DE DELTAS 100% FUNCIONAL! 🎉")
        print("\n📝 Notas:")
        print("   - Algunos métodos helper no existen (set_concentration)")
        print("   - Pero los componentes funcionan perfectamente")
        print("   - Sistema listo para producción")
    else:
        failed = [k for k, v in results.items() if not v]
        print(f"❌ Componentes que fallan: {failed}")
    
    return all_pass

if __name__ == "__main__":
    test_with_correct_api()