#!/usr/bin/env python3
"""
🔍 VERIFICADOR DE INDEPENDENCIA DE COMPONENTES
Asegura que todos los componentes funcionen sin dependencias
"""

import os
import sys
import numpy as np

current_dir = os.getcwd()
if 'trajectory_hub' in current_dir:
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

os.environ['DISABLE_OSC'] = '1'

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

print("""
================================================================================
🔍 VERIFICANDO INDEPENDENCIA DE COMPONENTES
================================================================================
""")

def test_component_independence():
    """Prueba que cada componente funcione independientemente."""
    
    results = {
        "concentracion_sola": False,
        "rotacion_ms_sola": False,
        "trayectorias_is_sola": False,
        "concentracion_con_rotacion": False,
        "concentracion_con_is": False,
        "rotacion_con_is": False,
        "todo_junto": False
    }
    
    try:
        # Test 1: Solo concentración
        print("\n1️⃣ TEST: Solo Concentración")
        print("-" * 50)
        engine = EnhancedTrajectoryEngine(max_sources=4, fps=60)
        macro_id = engine.create_macro("test1", source_count=4, formation="grid", spacing=4.0)
        
        pos_before = engine._source_motions[0].state.position.copy()
        engine.set_macro_concentration(macro_id, 0.8)
        
        for _ in range(30):
            engine.update(1/60)
            
        pos_after = engine._source_motions[0].state.position
        movement = np.linalg.norm(pos_after - pos_before)
        
        if movement > 0.1:
            print(f"✅ Concentración funciona sola (movimiento: {movement:.2f})")
            results["concentracion_sola"] = True
        else:
            print("❌ Concentración NO funciona sola")
            
        # Test 2: Solo rotación MS
        print("\n2️⃣ TEST: Solo Rotación Algorítmica MS")
        print("-" * 50)
        engine = EnhancedTrajectoryEngine(max_sources=4, fps=60)
        macro_id = engine.create_macro("test2", source_count=4, formation="line", spacing=2.0)
        
        # Aplicar rotación
        if hasattr(engine, 'set_macro_algorithmic_rotation'):
            engine.set_macro_algorithmic_rotation(macro_id, 
                angular_velocity={'yaw': 45.0, 'pitch': 0.0, 'roll': 0.0})
            
            pos_before = engine._source_motions[0].state.position.copy()
            
            for _ in range(30):
                engine.update(1/60)
                
            pos_after = engine._source_motions[0].state.position
            movement = np.linalg.norm(pos_after - pos_before)
            
            if movement > 0.1:
                print(f"✅ Rotación MS funciona sola (movimiento: {movement:.2f})")
                results["rotacion_ms_sola"] = True
            else:
                print("❌ Rotación MS NO funciona sola")
        else:
            print("⚠️  Rotación algorítmica no implementada")
            
        # Test 3: Concentración + Rotación MS
        print("\n3️⃣ TEST: Concentración + Rotación MS")
        print("-" * 50)
        engine = EnhancedTrajectoryEngine(max_sources=4, fps=60)
        macro_id = engine.create_macro("test3", source_count=4, formation="grid", spacing=4.0)
        
        # Aplicar ambos
        engine.set_macro_concentration(macro_id, 0.5)
        if hasattr(engine, 'set_macro_algorithmic_rotation'):
            engine.set_macro_algorithmic_rotation(macro_id, 
                angular_velocity={'yaw': 30.0, 'pitch': 0.0, 'roll': 0.0})
        
        # Verificar que ambos efectos ocurren
        positions_before = [engine._source_motions[i].state.position.copy() for i in range(4)]
        center_before = np.mean(positions_before, axis=0)
        
        for _ in range(60):
            engine.update(1/60)
            
        positions_after = [engine._source_motions[i].state.position for i in range(4)]
        center_after = np.mean(positions_after, axis=0)
        
        # Verificar concentración (reducción de dispersión)
        disp_before = np.mean([np.linalg.norm(p - center_before) for p in positions_before])
        disp_after = np.mean([np.linalg.norm(p - center_after) for p in positions_after])
        
        # Verificar rotación (el centro se movió)
        center_movement = np.linalg.norm(center_after - center_before)
        
        if disp_after < disp_before * 0.8 and center_movement > 0.1:
            print(f"✅ Ambos funcionan juntos!")
            print(f"   Dispersión: {disp_before:.2f} → {disp_after:.2f}")
            print(f"   Centro movido: {center_movement:.2f}")
            results["concentracion_con_rotacion"] = True
        else:
            print("❌ Los componentes no funcionan bien juntos")
            
        # Test 4: Con trayectorias IS
        print("\n4️⃣ TEST: Rotación MS con Trayectorias IS activas")
        print("-" * 50)
        engine = EnhancedTrajectoryEngine(max_sources=4, fps=60)
        macro_id = engine.create_macro("test4", source_count=4, formation="line", spacing=2.0)
        
        # Configurar trayectorias individuales
        engine.configure_individual_trajectories(macro_id, mode=1)  # Todas iguales
        
        # Aplicar rotación MS
        if hasattr(engine, 'set_macro_algorithmic_rotation'):
            engine.set_macro_algorithmic_rotation(macro_id, 
                angular_velocity={'yaw': 60.0, 'pitch': 0.0, 'roll': 0.0})
            
            pos_before = engine._source_motions[0].state.position.copy()
            
            for _ in range(30):
                engine.update(1/60)
                
            pos_after = engine._source_motions[0].state.position
            movement = np.linalg.norm(pos_after - pos_before)
            
            if movement > 0.1:
                print(f"✅ Rotación MS funciona CON trayectorias IS (movimiento: {movement:.2f})")
                results["rotacion_con_is"] = True
            else:
                print("❌ Rotación MS bloqueada por trayectorias IS")
                
    except Exception as e:
        print(f"\n❌ Error en tests: {e}")
        import traceback
        traceback.print_exc()
        
    # Resumen
    print("\n" + "="*70)
    print("📊 RESUMEN DE INDEPENDENCIA:")
    print("="*70)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"{status} {test.replace('_', ' ').title()}")
        
    print(f"\nTotal: {passed_tests}/{total_tests} tests pasados")
    
    if passed_tests == total_tests:
        print("\n🎉 ¡TODOS LOS COMPONENTES SON INDEPENDIENTES!")
    else:
        print("\n⚠️  Aún hay dependencias que resolver")
        
    return results

if __name__ == "__main__":
    test_component_independence()
