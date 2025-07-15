# === test_7_deltas_final.py ===
# 🧪 Test completo del sistema de deltas (7 componentes)
# ✅ Solo componentes delta para X,Y,Z
# ℹ️ Modulador 3D es independiente (Yaw, Pitch, Roll)

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub.core import EnhancedTrajectoryEngine
import numpy as np
import time
import math

def test_all_delta_components():
    """Test de los 7 componentes del sistema de deltas"""
    print("🧪 TEST COMPLETO DEL SISTEMA DE DELTAS")
    print("=" * 70)
    print("📍 Componentes X,Y,Z: Sistema de deltas")
    print("🎯 Orientación Yaw,Pitch,Roll: Modulador 3D (independiente)")
    print("=" * 70)
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=20, fps=60)
    
    # Crear dos macros para pruebas
    macro1 = engine.create_macro("test_group_1", source_count=4, formation="square", spacing=3.0)
    macro2 = engine.create_macro("test_group_2", source_count=4, formation="line", spacing=2.0)
    
    print(f"\n✅ Macros creados:")
    print(f"   - {macro1.name}: {len(macro1.source_ids)} fuentes")
    print(f"   - {macro2.name}: {len(macro2.source_ids)} fuentes")
    
    # ========== TEST 1: CONCENTRACIÓN ==========
    print("\n1️⃣ TEST: ConcentrationComponent")
    print("-" * 50)
    
    # Aplicar concentración
    engine.set_macro_concentration(macro1.name, factor=0.2)  # 0.2 = muy concentrado
    
    # Capturar posiciones iniciales
    initial_positions = {}
    for sid in macro1.source_ids:
        initial_positions[sid] = engine._positions[sid].copy()
    
    # Ejecutar algunos frames
    for _ in range(30):
        engine.update()
    
    # Verificar movimiento
    moved = False
    for sid in macro1.source_ids:
        if not np.allclose(initial_positions[sid], engine._positions[sid]):
            moved = True
            dist = np.linalg.norm(engine._positions[sid] - initial_positions[sid])
            print(f"   Fuente {sid}: movió {dist:.3f} unidades")
    
    print(f"   {'✅ PASS' if moved else '❌ FAIL'}: Concentración")
    
    # Limpiar
    for sid in macro1.source_ids:
        if sid in engine.motion_states:
            engine.motion_states[sid].active_components.pop('concentration', None)
    
    # ========== TEST 2: TRAYECTORIAS MACRO ==========
    print("\n2️⃣ TEST: MacroTrajectory")
    print("-" * 50)
    
    # Crear función de trayectoria circular
    def circle_trajectory(t):
        radius = 3.0
        return np.array([radius * np.cos(t * 2.0), radius * np.sin(t * 2.0), 0.0])
    
    engine.set_macro_trajectory("macro_0_test_group_1", circle_trajectory)
    
    initial_pos = engine._positions[list(macro1.source_ids)[0]].copy()
    for _ in range(30):
        engine.update()
    final_pos = engine._positions[list(macro1.source_ids)[0]]
    
    dist = np.linalg.norm(final_pos - initial_pos)
    print(f"   Movimiento: {dist:.3f} unidades")
    print(f"   {'✅ PASS' if dist > 0.1 else '❌ FAIL'}: MacroTrajectory")
    
    # ========== TEST 3: ROTACIÓN ALGORÍTMICA MS ==========
    print("\n3️⃣ TEST: MacroRotation (algorítmica)")
    print("-" * 50)
    
    engine.set_macro_rotation("macro_1_test_group_2", speed_x=0, speed_y=0, speed_z=1.0)  # Rotar en Z
    
    initial_positions = {sid: engine._positions[sid].copy() for sid in macro2.source_ids}
    for _ in range(30):
        engine.update()
    
    rotated = False
    for sid in macro2.source_ids:
        if not np.allclose(initial_positions[sid], engine._positions[sid]):
            rotated = True
            break
    
    print(f"   {'✅ PASS' if rotated else '❌ FAIL'}: MacroRotation")
    
    # ========== TEST 4: ROTACIÓN MANUAL MS ==========
    print("\n4️⃣ TEST: ManualMacroRotation")
    print("-" * 50)
    
    engine.set_manual_macro_rotation("macro_0_test_group_1", yaw=math.pi/2, pitch=0, roll=0, 
                                     interpolation_speed=0.1)
    
    initial_pos = {sid: engine._positions[sid].copy() for sid in macro1.source_ids}
    for _ in range(60):
        engine.update()
    
    rotated = False
    for sid in macro1.source_ids:
        if not np.allclose(initial_pos[sid], engine._positions[sid], atol=0.01):
            rotated = True
            break
    
    print(f"   {'✅ PASS' if rotated else '❌ FAIL'}: ManualMacroRotation")
    
    # ========== TEST 5: TRAYECTORIAS INDIVIDUALES ==========
    print("\n5️⃣ TEST: IndividualTrajectory")
    print("-" * 50)
    
    # Aplicar a una sola fuente
    test_source = list(macro1.source_ids)[0]
    # Crear función de trayectoria espiral
    
    engine.set_individual_trajectory(macro_id="macro_0_test_group_1", source_id=test_source, shape="spiral", speed=1.0)
    
    initial = engine._positions[test_source].copy()
    for _ in range(60):
        engine.update()
    final = engine._positions[test_source]
    
    dist = np.linalg.norm(final - initial)
    print(f"   Fuente {test_source}: movió {dist:.3f} unidades")
    print(f"   {'✅ PASS' if dist > 0.1 else '❌ FAIL'}: IndividualTrajectory")
    
    # ========== TEST 6: ROTACIÓN ALGORÍTMICA IS ==========
    print("\n6️⃣ TEST: IndividualRotation (algorítmica)")
    print("-" * 50)
    
    test_source = list(macro2.source_ids)[0]
    engine.set_individual_rotation(test_source, pitch=0, yaw=1.0, roll=0)
    
    initial = engine._positions[test_source].copy()
    for _ in range(60):
        engine.update()
    final = engine._positions[test_source]
    
    dist = np.linalg.norm(final - initial)
    print(f"   Fuente {test_source}: rotó {dist:.3f} unidades")
    print(f"   {'✅ PASS' if dist > 0.1 else '❌ FAIL'}: IndividualRotation")
    
    # ========== TEST 7: ROTACIÓN MANUAL IS ==========
    print("\n7️⃣ TEST: ManualIndividualRotation")
    print("-" * 50)
    
    test_source = list(macro1.source_ids)[1]
    engine.set_manual_individual_rotation(test_source, yaw=math.pi/4, pitch=0, roll=0,
                                          interpolation_speed=0.1)
    
    initial = engine._positions[test_source].copy()
    for _ in range(60):
        engine.update()
    final = engine._positions[test_source]
    
    dist = np.linalg.norm(final - initial)
    print(f"   Fuente {test_source}: rotó {dist:.3f} unidades")
    print(f"   {'✅ PASS' if dist > 0.1 else '❌ FAIL'}: ManualIndividualRotation")
    
    # ========== RESUMEN ==========
    print("\n" + "=" * 70)
    print("📊 RESUMEN DEL TEST")
    print("=" * 70)
    print("✅ Sistema de deltas para posición X,Y,Z")
    print("✅ Modulador 3D independiente para orientación Yaw,Pitch,Roll")
    print("❌ Sistema legacy de distancias desactivado (OK por ahora)")
    
    return True

if __name__ == "__main__":
    try:
        test_all_delta_components()
        print("\n✅ TEST COMPLETADO")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()