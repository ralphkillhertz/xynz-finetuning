#!/usr/bin/env python3
"""
🧪 Test corregido con los enums correctos
⚡ Verifica el problema real de concentración
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_movement_modes():
    """Verificar qué modos de movimiento existen"""
    print("🔍 MODOS DE MOVIMIENTO DISPONIBLES:")
    print("="*50)
    
    try:
        from trajectory_hub.core.motion_components import TrajectoryMovementMode
        
        print("Modos disponibles:")
        for mode in TrajectoryMovementMode:
            print(f"   - {mode.name} = {mode.value}")
            
    except Exception as e:
        print(f"Error: {e}")

def test_trajectory_basic():
    """Test básico con valores correctos"""
    print("\n\n🧪 TEST BÁSICO DE TRAYECTORIAS")
    print("="*50)
    
    try:
        from trajectory_hub.core.motion_components import (
            SourceMotion, IndividualTrajectory, MotionState,
            TrajectoryMovementMode
        )
        import numpy as np
        
        # 1. Test directo de IndividualTrajectory
        print("\n1️⃣ Test de IndividualTrajectory:")
        traj = IndividualTrajectory()
        
        # Configurar trayectoria
        traj.set_trajectory('circle', center=np.array([0, 0, 0]), radius=1.0)
        
        # Usar el modo correcto - intentar varios
        try:
            # Intentar CONSTANT_VELOCITY
            traj.set_movement_mode(TrajectoryMovementMode.CONSTANT_VELOCITY, movement_speed=1.0)
            print("   ✅ Usando modo: CONSTANT_VELOCITY")
        except:
            try:
                # Intentar CONSTANT_SPEED
                traj.set_movement_mode(TrajectoryMovementMode.CONSTANT_SPEED, movement_speed=1.0)
                print("   ✅ Usando modo: CONSTANT_SPEED")
            except:
                # Usar el valor numérico directamente
                traj.set_movement_mode('velocity', movement_speed=1.0)
                print("   ✅ Usando modo: 'velocity' (string)")
        
        # Estado inicial
        state = MotionState(position=np.array([0, 0, 0]))
        print(f"   Fase inicial: {traj.position_on_trajectory:.3f}")
        print(f"   Enabled: {traj.enabled}")
        
        # Updates
        for i in range(3):
            new_state = traj.update(state, i * 0.016, 0.016)
            print(f"   Update {i+1}: fase={traj.position_on_trajectory:.3f}, pos={new_state.position}")
            state = new_state
        
        if traj.position_on_trajectory > 0:
            print("   ✅ Trayectoria avanza correctamente")
            return True
        else:
            print("   ❌ Trayectoria NO avanza")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_engine_integration():
    """Test con el engine completo"""
    print("\n\n🎯 TEST DE INTEGRACIÓN CON ENGINE")
    print("="*50)
    
    try:
        from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
        
        # Crear engine sin OSC
        engine = EnhancedTrajectoryEngine(osc_bridge=None)
        
        # Debug: Ver estado inicial del engine
        print(f"Engine time: {engine._time}")
        print(f"Engine dt: {engine.dt}")
        
        # Crear macro
        macro_id = engine.create_macro("test", 3)
        print(f"✅ Macro creado: {macro_id}")
        
        # Configurar trayectorias - usar string directamente
        engine.set_individual_trajectories(
            macro_id,
            {0: 'circle', 1: 'circle', 2: 'circle'},
            movement_mode='velocity',  # Usar string
            movement_speed=1.0
        )
        
        # Verificar configuración
        print("\n📊 Verificación de configuración:")
        for i in range(3):
            if i in engine._source_motions:
                motion = engine._source_motions[i]
                if 'individual_trajectory' in motion.components:
                    traj = motion.components['individual_trajectory']
                    print(f"   Fuente {i}:")
                    print(f"      - Enabled: {traj.enabled}")
                    print(f"      - Movement mode: {getattr(traj, 'movement_mode', 'N/A')}")
                    print(f"      - Speed: {getattr(traj, 'movement_speed', 'N/A')}")
                    print(f"      - Fase: {traj.position_on_trajectory}")
        
        # Updates con debug
        print("\n⏯️ Ejecutando updates con debug...")
        for update_num in range(3):
            print(f"\n--- Update {update_num + 1} ---")
            
            # Update del engine
            engine.update()
            
            # Verificar estado después del update
            for i in range(3):
                if i in engine._source_motions:
                    motion = engine._source_motions[i]
                    if 'individual_trajectory' in motion.components:
                        traj = motion.components['individual_trajectory']
                        print(f"   Fuente {i}: fase={traj.position_on_trajectory:.4f}")
        
        # Verificación final
        print("\n📊 Estado final:")
        movement_ok = False
        for i in range(3):
            if i in engine._source_motions:
                motion = engine._source_motions[i]
                if 'individual_trajectory' in motion.components:
                    traj = motion.components['individual_trajectory']
                    if traj.position_on_trajectory > 0:
                        movement_ok = True
                        print(f"   ✅ Fuente {i} se movió: fase={traj.position_on_trajectory:.4f}")
                    else:
                        print(f"   ❌ Fuente {i} NO se movió")
        
        return movement_ok
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_concentration_direct():
    """Test directo de concentración"""
    print("\n\n🎯 TEST DIRECTO DE CONCENTRACIÓN")
    print("="*50)
    
    try:
        from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
        import numpy as np
        
        # Crear engine
        engine = EnhancedTrajectoryEngine(osc_bridge=None)
        
        # Crear macro con más fuentes
        macro_id = engine.create_macro("concentration_test", 10)
        
        # Configurar trayectorias individuales
        trajectories = {i: 'circle' for i in range(10)}
        engine.set_individual_trajectories(
            macro_id,
            trajectories,
            movement_mode='velocity',
            movement_speed=1.0
        )
        
        print("✅ Configuración inicial completa")
        
        # Algunos updates para establecer movimiento
        print("\n⏯️ Estableciendo movimiento...")
        for _ in range(10):
            engine.update()
        
        # Aplicar concentración
        print("\n🎯 Aplicando concentración total (factor=0.0)...")
        try:
            engine.set_concentration_factor(macro_id, 0.0)
            print("✅ Concentración aplicada sin errores")
            
            # Verificar que se esté aplicando
            engine.update()
            print("✅ Update post-concentración ejecutado")
            
            # Toggle
            print("\n🔄 Toggle concentración...")
            engine.toggle_concentration(macro_id)
            print("✅ Toggle ejecutado")
            
            return True
            
        except Exception as e:
            print(f"❌ Error en concentración: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ Error general: {e}")
        return False

if __name__ == "__main__":
    print("🔍 TEST CORREGIDO DE CONCENTRACIÓN")
    print("="*70)
    
    # 1. Verificar modos disponibles
    check_movement_modes()
    
    # 2. Test básico
    basic_ok = test_trajectory_basic()
    
    # 3. Test con engine
    if basic_ok:
        engine_ok = test_engine_integration()
        
        # 4. Test de concentración
        if engine_ok:
            concentration_ok = test_concentration_direct()
        else:
            concentration_ok = False
    else:
        engine_ok = False
        concentration_ok = False
    
    # Resumen
    print("\n" + "="*70)
    print("📊 RESUMEN DE TESTS:")
    print(f"   1. Trayectoria básica: {'✅ OK' if basic_ok else '❌ FALLA'}")
    print(f"   2. Integración engine: {'✅ OK' if engine_ok else '❌ FALLA'}")
    print(f"   3. Concentración: {'✅ OK' if concentration_ok else '❌ FALLA'}")
    
    if not engine_ok and basic_ok:
        print("\n⚠️ El problema está en cómo el engine actualiza los componentes")