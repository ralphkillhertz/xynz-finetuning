# === test_delta_100.py ===
# 🎯 Test final para alcanzar 100% funcionalidad
# ⚡ Con todas las correcciones aplicadas

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub.core import EnhancedTrajectoryEngine
import numpy as np

def test_delta_system():
    """Test completo del sistema de deltas"""
    print("🚀 TEST SISTEMA DE DELTAS - OBJETIVO 100%")
    print("=" * 60)
    
    results = {"passed": 0, "failed": 0}
    
    # Test 1: Concentración
    print("\n1️⃣ TEST: Concentración")
    print("-" * 40)
    try:
        engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)
        macro = engine.create_macro("test_conc", 4, formation='square', spacing=3.0)
        
        print("Posiciones iniciales:")
        sids = list(macro.source_ids)[:4]
        for sid in sids:
            print(f"  Fuente {sid}: {engine._positions[sid]}")
        
        # Aplicar concentración con objeto macro
        engine.set_macro_concentration(macro, 0.5)
        
        # Simular más frames
        for _ in range(60):  # Más frames para ver movimiento
            engine.update()
        
        print("\nPosiciones finales:")
        moved = 0
        for sid in sids:
            pos = engine._positions[sid]
            print(f"  Fuente {sid}: {pos}")
            if np.linalg.norm(pos) < 2.0:  # Se acercaron al centro
                moved += 1
        
        if moved >= 3:
            print(f"✅ Concentración exitosa: {moved}/4 fuentes")
            results["passed"] += 1
        else:
            print(f"❌ Concentración no funcionó: solo {moved}/4 se movieron")
            results["failed"] += 1
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        results["failed"] += 1
    
    # Test 2: Trayectorias individuales
    print("\n2️⃣ TEST: Trayectorias Individuales")
    print("-" * 40)
    try:
        engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)
        macro = engine.create_macro("test_traj", 3, formation='line', spacing=3.0)
        
        # Configurar con objeto macro
        shapes = ['circle', 'spiral', 'figure8']
        sids = list(macro.source_ids)[:3]
        
        for i, sid in enumerate(sids):
            engine.set_individual_trajectory(
                macro, i, shapes[i],
                shape_params={'radius': 2.0},
                movement_mode='fix',
                speed=2.0
            )
        
        # Guardar posiciones iniciales
        initial = {sid: engine._positions[sid].copy() for sid in sids}
        
        # Simular
        for _ in range(120):  # Más frames
            engine.update()
        
        # Verificar movimiento
        moved = 0
        for i, sid in enumerate(sids):
            dist = np.linalg.norm(engine._positions[sid] - initial[sid])
            if dist > 0.5:
                moved += 1
                print(f"✅ Fuente {sid} ({shapes[i]}) se movió {dist:.2f} unidades")
            else:
                print(f"❌ Fuente {sid} ({shapes[i]}) no se movió: {dist:.2f}")
        
        if moved >= 2:
            print(f"✅ Trayectorias funcionan: {moved}/3")
            results["passed"] += 1
        else:
            results["failed"] += 1
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        results["failed"] += 1
    
    # Test 3: Rotación Macro
    print("\n3️⃣ TEST: Rotación Macro")
    print("-" * 40)
    try:
        engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)
        macro = engine.create_macro("test_rot", 3, formation='line', spacing=3.0)
        
        # Estabilizar
        for _ in range(10):
            engine.update()
        
        # Guardar ángulo inicial
        sid = list(macro.source_ids)[0]
        initial_angle = np.arctan2(engine._positions[sid][1], engine._positions[sid][0])
        
        # Aplicar rotación con objeto macro
        engine.set_macro_rotation(macro, speed_x=0, speed_y=2.0, speed_z=0)
        
        # Simular
        for _ in range(60):
            engine.update()
        
        # Verificar rotación
        final_angle = np.arctan2(engine._positions[sid][1], engine._positions[sid][0])
        rotation = final_angle - initial_angle
        
        if abs(rotation) > 0.5:
            print(f"✅ Rotación detectada: {np.degrees(rotation):.1f}°")
            results["passed"] += 1
        else:
            print(f"❌ Sin rotación significativa: {np.degrees(rotation):.1f}°")
            results["failed"] += 1
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        results["failed"] += 1
    
    # Test 4: Rotación Individual
    print("\n4️⃣ TEST: Rotación Individual")
    print("-" * 40)
    try:
        engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)
        sid = 8
        engine.create_source(sid)
        engine._positions[sid] = np.array([3.0, 0.0, 0.0])
        if sid in engine.motion_states:
            engine.motion_states[sid].state.position = np.array([3.0, 0.0, 0.0])
        
        # Aplicar rotación
        engine.set_individual_rotation(sid, speed_x=0.0, speed_y=3.0, speed_z=0.0)
        
        # Simular
        for _ in range(60):
            engine.update()
        
        final_angle = np.degrees(np.arctan2(engine._positions[sid][1], engine._positions[sid][0]))
        
        if abs(final_angle) > 30:
            print(f"✅ Rotación individual: {final_angle:.1f}°")
            results["passed"] += 1
        else:
            print(f"❌ Rotación insuficiente: {final_angle:.1f}°")
            results["failed"] += 1
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        results["failed"] += 1
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN FINAL")
    print("=" * 60)
    total = results["passed"] + results["failed"]
    print(f"✅ Pasados: {results['passed']}/{total}")
    print(f"❌ Fallados: {results['failed']}/{total}")
    
    if total > 0:
        success_rate = (results['passed'] / total) * 100
        print(f"📈 Tasa de éxito: {success_rate:.1f}%")
        
        if success_rate == 100:
            print("\n🎉 ¡SISTEMA DE DELTAS 100% FUNCIONAL!")
        elif success_rate >= 75:
            print("\n✅ Sistema operativo")
        else:
            print("\n⚠️ Sistema necesita atención")

if __name__ == "__main__":
    test_delta_system()
