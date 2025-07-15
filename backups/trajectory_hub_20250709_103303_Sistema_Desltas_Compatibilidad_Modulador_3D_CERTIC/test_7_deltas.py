# === test_7_deltas.py ===
# 🧪 Test de los 7 componentes del sistema de deltas
# ✅ MS Trayectorias, MS Rotaciones, IS Trayectorias, IS Rotaciones, Concentración

import numpy as np
from trajectory_hub.core import EnhancedTrajectoryEngine

def test_7_deltas():
    """Test completo del sistema de deltas"""
    
    print("🧪 TEST SISTEMA DE DELTAS - 7 COMPONENTES")
    print("=" * 70)
    
    engine = EnhancedTrajectoryEngine(max_sources=50, fps=60)
    results = {}
    
    try:
        # 1. CONCENTRACIÓN
        print("\n1️⃣ Test CONCENTRACIÓN...")
        macro1 = engine.create_macro("conc", 4, formation="square", spacing=5.0)
        initial_pos = engine._positions[0].copy()
        
        engine.set_distance_control("conc", mode="convergent")
        for _ in range(30):
            engine.update()
            
        final_pos = engine._positions[0]
        moved = np.linalg.norm(final_pos - initial_pos) > 0.1
        results["concentracion"] = moved
        print(f"   {'✅' if moved else '❌'} Concentración: {moved}")
        
        # 2. MS TRAYECTORIAS
        print("\n2️⃣ Test MS TRAYECTORIAS...")
        macro2 = engine.create_macro("ms_traj", 3)
        engine.set_macro_trajectory("ms_traj", "circle", speed=2.0)
        
        initial = engine._positions[10].copy()
        for _ in range(30):
            engine.update()
        moved = np.linalg.norm(engine._positions[10] - initial) > 0.5
        results["ms_trayectorias"] = moved
        print(f"   {'✅' if moved else '❌'} MS Trayectorias: {moved}")
        
        # 3. MS ROTACIÓN ALGORÍTMICA
        print("\n3️⃣ Test MS ROTACIÓN ALGORÍTMICA...")
        macro3 = engine.create_macro("ms_rot_algo", 4, formation="square")
        engine.set_macro_rotation("ms_rot_algo", speed_x=0, speed_y=0, speed_z=1.0)
        
        angle_before = np.arctan2(engine._positions[20][1], engine._positions[20][0])
        for _ in range(30):
            engine.update()
        angle_after = np.arctan2(engine._positions[20][1], engine._positions[20][0])
        rotated = abs(angle_after - angle_before) > 0.1
        results["ms_rot_algo"] = rotated
        print(f"   {'✅' if rotated else '❌'} MS Rot Algorítmica: {rotated}")
        
        # 4. MS ROTACIÓN MANUAL
        print("\n4️⃣ Test MS ROTACIÓN MANUAL...")
        macro4 = engine.create_macro("ms_rot_man", 2)
        engine.set_manual_macro_rotation("ms_rot_man", yaw=1.57, pitch=0, roll=0, 
                                       interpolation_speed=0.1)
        
        pos_before = engine._positions[30].copy()
        for _ in range(60):
            engine.update()
        pos_after = engine._positions[30]
        rotated = np.linalg.norm(pos_after - pos_before) > 0.1
        results["ms_rot_manual"] = rotated
        print(f"   {'✅' if rotated else '❌'} MS Rot Manual: {rotated}")
        
        # 5. IS TRAYECTORIAS
        print("\n5️⃣ Test IS TRAYECTORIAS...")
        sid = 40
        engine.create_source(sid)
        engine.set_individual_trajectory(sid, shape="spiral", scale=2.0, speed=1.0)
        
        initial = engine._positions[sid].copy()
        for _ in range(30):
            engine.update()
        moved = np.linalg.norm(engine._positions[sid] - initial) > 0.1
        results["is_trayectorias"] = moved
        print(f"   {'✅' if moved else '❌'} IS Trayectorias: {moved}")
        
        # 6. IS ROTACIÓN ALGORÍTMICA
        print("\n6️⃣ Test IS ROTACIÓN ALGORÍTMICA...")
        sid2 = 41
        engine.create_source(sid2)
        engine._positions[sid2] = np.array([3.0, 0.0, 0.0])
        engine.set_individual_rotation(sid2, speed_x=0, speed_y=0, speed_z=2.0)
        
        angle_before = np.arctan2(engine._positions[sid2][1], engine._positions[sid2][0])
        for _ in range(30):
            engine.update()
        angle_after = np.arctan2(engine._positions[sid2][1], engine._positions[sid2][0])
        rotated = abs(angle_after - angle_before) > 0.1
        results["is_rot_algo"] = rotated
        print(f"   {'✅' if rotated else '❌'} IS Rot Algorítmica: {rotated}")
        
        # 7. IS ROTACIÓN MANUAL
        print("\n7️⃣ Test IS ROTACIÓN MANUAL...")
        sid3 = 42
        engine.create_source(sid3)
        engine._positions[sid3] = np.array([0.0, 3.0, 0.0])
        engine.set_manual_individual_rotation(sid3, yaw=3.14, pitch=0, roll=0,
                                            interpolation_speed=0.1)
        
        pos_before = engine._positions[sid3].copy()
        for _ in range(60):
            engine.update()
        pos_after = engine._positions[sid3]
        moved = np.linalg.norm(pos_after - pos_before) > 0.1
        results["is_rot_manual"] = moved
        print(f"   {'✅' if moved else '❌'} IS Rot Manual: {moved}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # RESUMEN
    print("\n" + "=" * 70)
    print("📊 RESUMEN SISTEMA DE DELTAS:")
    print("=" * 70)
    
    total = len(results)
    passed = sum(results.values())
    
    for component, ok in results.items():
        print(f"   {component.ljust(20)} {'✅ PASS' if ok else '❌ FAIL'}")
    
    print(f"\n   TOTAL: {passed}/{total} ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n🎉 ¡SISTEMA DE DELTAS 100% FUNCIONAL!")
    
    return passed == total

if __name__ == "__main__":
    test_7_deltas()
