# === test_delta_system_complete.py ===
# 🧪 Test exhaustivo del sistema de deltas
# ⚡ Verifica que todos los componentes funcionan sin conflictos

import time
import numpy as np
from trajectory_hub.core import EnhancedTrajectoryEngine

def test_delta_system():
    """Test completo del sistema de deltas"""
    
    print("🧪 TEST EXHAUSTIVO DEL SISTEMA DE DELTAS")
    print("=" * 70)
    
    # Crear engine
    print("\n1️⃣ Creando engine...")
    engine = EnhancedTrajectoryEngine(max_sources=50, fps=60)
    print("   ✅ Engine creado")
    
    # Test de cada componente
    test_results = {
        "concentration": False,
        "individual_trajectory": False,
        "macro_trajectory": False,
        "macro_rotation": False,
        "manual_macro_rotation": False,
        "individual_rotation": False,
        "manual_individual_rotation": False
    }
    
    try:
        # =================================================================
        # TEST 1: CONCENTRACIÓN
        # =================================================================
        print("\n2️⃣ TEST DE CONCENTRACIÓN...")
        
        # Crear macro en formación amplia
        macro = engine.create_macro("test_concentration", 5, formation="line", spacing=3.0)
        source_ids = list(macro.source_ids)
        
        # Guardar posiciones iniciales
        initial_positions = {}
        for sid in source_ids:
            initial_positions[sid] = engine._positions[sid].copy()
        
        print(f"   Posiciones iniciales: {initial_positions}")
        
        # Aplicar concentración
        engine.set_distance_control("test_concentration", mode="convergent")
        
        # Simular varios frames
        for _ in range(60):  # 1 segundo
            engine.update()
        
        # Verificar que se concentraron
        concentrated = True
        for sid in source_ids:
            dist = np.linalg.norm(engine._positions[sid])
            if dist > 1.0:  # Deberían estar cerca del centro
                concentrated = False
                break
        
        test_results["concentration"] = concentrated
        print(f"   {'✅' if concentrated else '❌'} Concentración: {concentrated}")
        
        # =================================================================
        # TEST 2: TRAYECTORIAS INDIVIDUALES
        # =================================================================
        print("\n3️⃣ TEST DE TRAYECTORIAS INDIVIDUALES...")
        
        # Crear nuevo macro
        macro2 = engine.create_macro("test_is", 3)
        source_ids2 = list(macro2.source_ids)
        
        # Aplicar trayectorias diferentes a cada fuente
        shapes = ["circle", "spiral", "figure8"]
        for i, (sid, shape) in enumerate(zip(source_ids2, shapes)):
            engine.set_individual_trajectory(sid, shape=shape, scale=2.0, speed=1.0)
        
        # Guardar posiciones iniciales
        initial_pos_is = {}
        for sid in source_ids2:
            initial_pos_is[sid] = engine._positions[sid].copy()
        
        # Simular movimiento
        for _ in range(30):
            engine.update()
        
        # Verificar que se movieron
        moved_is = True
        for sid in source_ids2:
            dist_moved = np.linalg.norm(engine._positions[sid] - initial_pos_is[sid])
            if dist_moved < 0.1:
                moved_is = False
                break
        
        test_results["individual_trajectory"] = moved_is
        print(f"   {'✅' if moved_is else '❌'} Trayectorias IS: {moved_is}")
        
        # =================================================================
        # TEST 3: TRAYECTORIAS MACRO
        # =================================================================
        print("\n4️⃣ TEST DE TRAYECTORIAS MACRO...")
        
        # Crear macro para trayectoria
        macro3 = engine.create_macro("test_macro_traj", 4, formation="square")
        source_ids3 = list(macro3.source_ids)
        
        # Aplicar trayectoria circular al macro
        engine.set_macro_trajectory("test_macro_traj", "circle", speed=2.0)
        
        # Posiciones iniciales
        initial_macro = {}
        for sid in source_ids3:
            initial_macro[sid] = engine._positions[sid].copy()
        
        # Simular
        for _ in range(30):
            engine.update()
        
        # Verificar movimiento
        moved_macro = True
        for sid in source_ids3:
            dist_moved = np.linalg.norm(engine._positions[sid] - initial_macro[sid])
            if dist_moved < 0.5:
                moved_macro = False
                break
        
        test_results["macro_trajectory"] = moved_macro
        print(f"   {'✅' if moved_macro else '❌'} Trayectoria Macro: {moved_macro}")
        
        # =================================================================
        # TEST 4: ROTACIÓN MACRO ALGORÍTMICA
        # =================================================================
        print("\n5️⃣ TEST DE ROTACIÓN MACRO ALGORÍTMICA...")
        
        # Crear macro en cruz
        macro4 = engine.create_macro("test_rotation", 4, formation="square", spacing=3.0)
        source_ids4 = list(macro4.source_ids)
        
        # Aplicar rotación algorítmica
        engine.set_macro_rotation("test_rotation", speed_x=0, speed_y=0, speed_z=1.0)
        
        # Guardar ángulos iniciales
        initial_angles = {}
        for sid in source_ids4:
            pos = engine._positions[sid]
            initial_angles[sid] = np.arctan2(pos[1], pos[0])
        
        # Simular
        for _ in range(30):
            engine.update()
        
        # Verificar rotación
        rotated = True
        for sid in source_ids4:
            pos = engine._positions[sid]
            current_angle = np.arctan2(pos[1], pos[0])
            angle_diff = abs(current_angle - initial_angles[sid])
            if angle_diff < 0.1:  # Debería haber rotado
                rotated = False
                break
        
        test_results["macro_rotation"] = rotated
        print(f"   {'✅' if rotated else '❌'} Rotación Macro: {rotated}")
        
        # =================================================================
        # TEST 5: ROTACIÓN MACRO MANUAL
        # =================================================================
        print("\n6️⃣ TEST DE ROTACIÓN MACRO MANUAL...")
        
        # Crear macro
        macro5 = engine.create_macro("test_manual_rot", 4, formation="line", spacing=2.0)
        source_ids5 = list(macro5.source_ids)
        
        # Aplicar rotación manual 90 grados
        engine.set_manual_macro_rotation("test_manual_rot", yaw=1.57, pitch=0, roll=0, 
                                       interpolation_speed=0.1)
        
        # Posiciones iniciales
        initial_manual = engine._positions[source_ids5[0]].copy()
        
        # Simular
        for _ in range(60):
            engine.update()
        
        # Verificar rotación de 90 grados
        final_pos = engine._positions[source_ids5[0]]
        angle_moved = np.arctan2(final_pos[1], final_pos[0])
        manual_rotated = abs(angle_moved - 1.57) < 0.2  # Cerca de 90 grados
        
        test_results["manual_macro_rotation"] = manual_rotated
        print(f"   {'✅' if manual_rotated else '❌'} Rotación Manual MS: {manual_rotated}")
        
        # =================================================================
        # TEST 6: ROTACIÓN INDIVIDUAL ALGORÍTMICA
        # =================================================================
        print("\n7️⃣ TEST DE ROTACIÓN INDIVIDUAL ALGORÍTMICA...")
        
        # Usar una fuente individual
        sid_rot = 20
        engine.create_source(sid_rot)
        engine._positions[sid_rot] = np.array([3.0, 0.0, 0.0])
        
        # Aplicar rotación individual
        engine.set_individual_rotation(sid_rot, speed_x=0, speed_y=0, speed_z=2.0)
        
        initial_angle_is = np.arctan2(engine._positions[sid_rot][1], 
                                     engine._positions[sid_rot][0])
        
        # Simular
        for _ in range(30):
            engine.update()
        
        # Verificar
        final_angle_is = np.arctan2(engine._positions[sid_rot][1], 
                                   engine._positions[sid_rot][0])
        is_rotated = abs(final_angle_is - initial_angle_is) > 0.5
        
        test_results["individual_rotation"] = is_rotated
        print(f"   {'✅' if is_rotated else '❌'} Rotación IS Algo: {is_rotated}")
        
        # =================================================================
        # TEST 7: ROTACIÓN INDIVIDUAL MANUAL
        # =================================================================
        print("\n8️⃣ TEST DE ROTACIÓN INDIVIDUAL MANUAL...")
        
        # Otra fuente
        sid_manual = 21
        engine.create_source(sid_manual)
        engine._positions[sid_manual] = np.array([0.0, 3.0, 0.0])
        
        # Rotación manual 180 grados
        engine.set_manual_individual_rotation(sid_manual, yaw=3.14, pitch=0, roll=0,
                                            interpolation_speed=0.1)
        
        initial_manual_is = engine._positions[sid_manual].copy()
        
        # Simular
        for _ in range(60):
            engine.update()
        
        # Verificar (debería estar cerca de [0, -3, 0])
        final_manual_is = engine._positions[sid_manual]
        expected = np.array([0.0, -3.0, 0.0])
        distance_to_expected = np.linalg.norm(final_manual_is - expected)
        manual_is_rotated = distance_to_expected < 1.0
        
        test_results["manual_individual_rotation"] = manual_is_rotated
        print(f"   {'✅' if manual_is_rotated else '❌'} Rotación Manual IS: {manual_is_rotated}")
        
        # =================================================================
        # TEST COMBINADO: TODOS LOS COMPONENTES JUNTOS
        # =================================================================
        print("\n9️⃣ TEST COMBINADO - TODOS LOS COMPONENTES...")
        
        # Crear macro con todo
        macro_all = engine.create_macro("test_all", 8, formation="circle", spacing=5.0)
        
        # Aplicar múltiples efectos
        engine.set_macro_trajectory("test_all", "spiral", speed=1.0)
        engine.set_distance_control("test_all", mode="breathing", min_dist=2.0, max_dist=8.0)
        engine.set_macro_rotation("test_all", speed_x=0.5, speed_y=0.5, speed_z=0.5)
        
        # Algunas fuentes con trayectorias individuales
        all_ids = list(macro_all.source_ids)
        for i in range(0, len(all_ids), 2):
            engine.set_individual_trajectory(all_ids[i], shape="vibration", amplitude=0.5)
        
        # Simular
        errors = 0
        for frame in range(120):  # 2 segundos
            try:
                engine.update()
            except Exception as e:
                print(f"   ❌ Error en frame {frame}: {e}")
                errors += 1
                if errors > 5:
                    break
        
        combined_ok = errors == 0
        print(f"   {'✅' if combined_ok else '❌'} Test combinado: {'Sin errores' if combined_ok else f'{errors} errores'}")
        
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
    
    # =================================================================
    # RESUMEN FINAL
    # =================================================================
    print("\n" + "=" * 70)
    print("📊 RESUMEN DE RESULTADOS")
    print("=" * 70)
    
    total_tests = len(test_results)
    passed = sum(test_results.values())
    
    for component, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {component.ljust(30)} {status}")
    
    print(f"\n   TOTAL: {passed}/{total_tests} tests pasados ({passed/total_tests*100:.1f}%)")
    
    if passed == total_tests:
        print("\n🎉 ¡SISTEMA DE DELTAS 100% FUNCIONAL!")
    else:
        print(f"\n⚠️ Sistema de deltas al {passed/total_tests*100:.1f}% funcional")
        print("   Revisar componentes que fallaron")
    
    return passed == total_tests

if __name__ == "__main__":
    success = test_delta_system()
    exit(0 if success else 1)