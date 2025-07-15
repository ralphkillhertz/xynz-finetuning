# === test_delta_system_final.py ===
# 🎯 Test final del sistema de deltas
# ⚡ Verificación completa de funcionalidad

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub.core import EnhancedTrajectoryEngine
import numpy as np
import time

def test_delta_system():
    """Test completo del sistema de deltas"""
    print("🚀 TEST FINAL SISTEMA DE DELTAS")
    print("=" * 60)
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=20, fps=60)
    results = {"passed": 0, "failed": 0}
    
    # Test 1: Concentración con formación adecuada
    print("\n1️⃣ TEST: Concentración")
    print("-" * 40)
    try:
        # Crear macro con spacing adecuado
        macro = engine.create_macro("test_conc", 4, formation='square', spacing=3.0)
        
        # Verificar posiciones iniciales
        print("Posiciones iniciales:")
        for i in range(4):
            print(f"  Fuente {i}: {engine._positions[i]}")
        
        # Aplicar concentración
        engine.set_macro_concentration(macro, 0.5)
        
        # Simular
        for _ in range(30):
            engine.update()
        
        # Verificar
        print("\nPosiciones finales:")
        moved = 0
        for i in range(4):
            pos = engine._positions[i]
            print(f"  Fuente {i}: {pos}")
            if np.linalg.norm(pos) < 2.5:  # Se acercaron al centro
                moved += 1
        
        if moved >= 3:
            print(f"✅ Concentración exitosa: {moved}/4 fuentes")
            results["passed"] += 1
        else:
            print(f"❌ Concentración falló")
            results["failed"] += 1
            
    except Exception as e:
        print(f"❌ Error: {e}")
        results["failed"] += 1
    
    # Test 2: Trayectorias individuales
    print("\n2️⃣ TEST: Trayectorias Individuales")
    print("-" * 40)
    try:
        macro = engine.create_macro("test_traj", 3, formation='line', spacing=3.0)
        
        # Configurar trayectorias
        for i in range(3):
            shape = ['circle', 'spiral', 'figure8'][i]
            engine.set_individual_trajectory(
                macro, i, shape,
                shape_params={'radius': 2.0},
                movement_mode='fix',
                speed=2.0
            )
        
        # Simular
        initial = [engine._positions[i].copy() for i in range(3)]
        
        for _ in range(60):
            engine.update()
        
        # Verificar movimiento
        moved = 0
        for i in range(3):
            dist = np.linalg.norm(engine._positions[i] - initial[i])
            if dist > 1.0:
                moved += 1
                print(f"✅ Fuente {i} se movió {dist:.2f} unidades")
        
        if moved >= 2:
            print(f"✅ Trayectorias funcionan: {moved}/3")
            results["passed"] += 1
        else:
            results["failed"] += 1
            
    except Exception as e:
        print(f"❌ Error: {e}")
        results["failed"] += 1
    
    # Test 3: Rotación Macro
    print("\n3️⃣ TEST: Rotación Macro")
    print("-" * 40)
    try:
        macro = engine.create_macro("test_rot", 3, formation='line', spacing=3.0)
        
        # Estabilizar
        for _ in range(5):
            engine.update()
        
        # Aplicar rotación
        engine.set_macro_rotation(macro, speed_x=0, speed_y=1.0, speed_z=0)
        
        # Simular
        initial_angle = np.arctan2(engine._positions[0][1], engine._positions[0][0])
        
        for _ in range(30):
            engine.update()
        
        final_angle = np.arctan2(engine._positions[0][1], engine._positions[0][0])
        rotation = final_angle - initial_angle
        
        if abs(rotation) > 0.1:
            print(f"✅ Rotación detectada: {np.degrees(rotation):.1f}°")
            results["passed"] += 1
        else:
            print(f"❌ Sin rotación significativa")
            results["failed"] += 1
            
    except Exception as e:
        print(f"❌ Error: {e}")
        results["failed"] += 1
    
    # Test 4: Rotación Individual
    print("\n4️⃣ TEST: Rotación Individual")
    print("-" * 40)
    try:
        # Crear fuente individual
        sid = 10
        engine.create_source(sid)
        engine._positions[sid] = np.array([3.0, 0.0, 0.0])
        if sid in engine.motion_states:
            engine.motion_states[sid].state.position = np.array([3.0, 0.0, 0.0])
        
        # Aplicar rotación
        engine.set_individual_rotation(sid, speed_y=2.0)
        
        # Simular
        for _ in range(30):
            engine.update()
        
        angle = np.degrees(np.arctan2(engine._positions[sid][1], engine._positions[sid][0]))
        
        if abs(angle) > 20:
            print(f"✅ Rotación individual: {angle:.1f}°")
            results["passed"] += 1
        else:
            print(f"❌ Rotación insuficiente")
            results["failed"] += 1
            
    except Exception as e:
        print(f"❌ Error: {e}")
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
