#!/usr/bin/env python3
"""
🧪 Test directo de concentración sin dependencias externas
⚡ Verifica si las trayectorias se mueven correctamente
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_trajectory_movement():
    """Test básico del movimiento de trayectorias"""
    print("🧪 TEST DE MOVIMIENTO DE TRAYECTORIAS")
    print("="*50)
    
    try:
        from trajectory_hub.core.motion_components import (
            SourceMotion, IndividualTrajectory, MotionState,
            TrajectoryMovementMode
        )
        import numpy as np
        
        # 1. Test de IndividualTrajectory directamente
        print("\n1️⃣ Test de IndividualTrajectory solo:")
        traj = IndividualTrajectory()
        
        # Configurar trayectoria
        traj.set_trajectory('circle', center=np.array([0, 0, 0]), radius=1.0)
        traj.set_movement_mode(TrajectoryMovementMode.VELOCITY, movement_speed=1.0)
        
        # Estado inicial
        state = MotionState(position=np.array([0, 0, 0]))
        print(f"   Estado inicial - fase: {traj.position_on_trajectory:.3f}")
        
        # Update directo
        new_state = traj.update(state, 0.0, 0.016)
        print(f"   Después de update - fase: {traj.position_on_trajectory:.3f}")
        print(f"   Nueva posición: {new_state.position}")
        
        if traj.position_on_trajectory > 0:
            print("   ✅ IndividualTrajectory funciona correctamente")
        else:
            print("   ❌ IndividualTrajectory NO avanza")
        
        # 2. Test de SourceMotion con IndividualTrajectory
        print("\n2️⃣ Test de SourceMotion con IndividualTrajectory:")
        motion = SourceMotion(source_id=0)
        
        # Crear y agregar trayectoria
        traj2 = IndividualTrajectory()
        traj2.set_trajectory('circle', center=np.array([5, 0, 0]), radius=2.0)
        traj2.set_movement_mode(TrajectoryMovementMode.VELOCITY, movement_speed=2.0)
        
        motion.add_component('individual_trajectory', traj2)
        
        print(f"   Estado inicial - fase: {traj2.position_on_trajectory:.3f}")
        print(f"   Posición inicial: {motion.state.position}")
        
        # Updates
        for i in range(3):
            pos, ori, aper = motion.update(i * 0.016, 0.016)
            print(f"\n   Update {i+1}:")
            print(f"   - Fase: {traj2.position_on_trajectory:.3f}")
            print(f"   - Posición: {pos}")
        
        if traj2.position_on_trajectory > 0:
            print("\n   ✅ SourceMotion propaga updates correctamente")
        else:
            print("\n   ❌ SourceMotion NO propaga updates")
            
        return traj2.position_on_trajectory > 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_concentration_scenario():
    """Test del escenario de concentración"""
    print("\n\n🎯 TEST DE ESCENARIO DE CONCENTRACIÓN")
    print("="*50)
    
    try:
        from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
        
        # Crear engine sin OSC
        engine = EnhancedTrajectoryEngine(osc_bridge=None)
        
        # Crear macro
        macro_id = engine.create_macro("test_conc", 3)
        print(f"✅ Macro creado: {macro_id}")
        
        # Configurar trayectorias individuales
        engine.set_individual_trajectories(
            macro_id,
            {0: 'circle', 1: 'circle', 2: 'circle'},
            movement_mode='velocity',
            movement_speed=1.0
        )
        print("✅ Trayectorias configuradas")
        
        # Estado inicial
        print("\n📊 Estado inicial:")
        for i in range(3):
            if i in engine._source_motions:
                motion = engine._source_motions[i]
                if 'individual_trajectory' in motion.components:
                    traj = motion.components['individual_trajectory']
                    print(f"   Fuente {i}: fase={traj.position_on_trajectory:.3f}, enabled={traj.enabled}")
        
        # Updates
        print("\n⏯️ Ejecutando 5 updates...")
        for _ in range(5):
            engine.update()
        
        # Estado final
        print("\n📊 Estado después de updates:")
        movement_detected = False
        for i in range(3):
            if i in engine._source_motions:
                motion = engine._source_motions[i]
                if 'individual_trajectory' in motion.components:
                    traj = motion.components['individual_trajectory']
                    print(f"   Fuente {i}: fase={traj.position_on_trajectory:.3f}")
                    if traj.position_on_trajectory > 0:
                        movement_detected = True
        
        if movement_detected:
            print("\n✅ Sistema funciona - las trayectorias avanzan")
            
            # Test de concentración
            print("\n🎯 Probando concentración...")
            engine.set_concentration_factor(macro_id, 0.0)
            print("✅ Concentración aplicada sin errores")
        else:
            print("\n❌ Sistema NO funciona - las trayectorias no avanzan")
            
        return movement_detected
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 TEST DIRECTO DE CONCENTRACIÓN")
    print("="*70)
    
    # Ejecutar tests
    basic_ok = test_trajectory_movement()
    
    if basic_ok:
        concentration_ok = test_concentration_scenario()
        
        print("\n" + "="*70)
        print("📊 RESUMEN:")
        print(f"   Movimiento básico: {'✅ OK' if basic_ok else '❌ FALLA'}")
        print(f"   Sistema completo: {'✅ OK' if concentration_ok else '❌ FALLA'}")
    else:
        print("\n❌ El sistema básico no funciona, revisar motion_components.py")