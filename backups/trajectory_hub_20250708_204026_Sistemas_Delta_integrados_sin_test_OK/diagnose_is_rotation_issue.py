# === diagnose_is_rotation_issue.py ===
# 🔍 Diagnóstico profundo de rotaciones IS
# ⚡ Por qué no se mueven las fuentes

import numpy as np
from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import IndividualRotation, ManualIndividualRotation

def diagnose_is_rotations():
    """Diagnóstico completo del sistema de rotaciones IS"""
    
    print("🔍 DIAGNÓSTICO: ROTACIONES INDIVIDUAL SOURCE")
    print("=" * 60)
    
    # 1. Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=10, fps=60, enable_modulator=False)
    
    # 2. Crear una fuente
    print("\n1️⃣ Creando fuente de prueba...")
    motion = engine.create_source(0)
    engine._positions[0] = np.array([3.0, 0.0, 0.0])
    print(f"   Posición inicial: {engine._positions[0]}")
    
    # 3. Verificar motion_states
    print("\n2️⃣ Verificando motion_states...")
    if 0 in engine.motion_states:
        state = engine.motion_states[0]
        print(f"   ✅ Motion state existe")
        print(f"   Estado: {state}")
        print(f"   Componentes activos: {state.motion.active_components}")
    else:
        print("   ❌ No hay motion state para fuente 0")
        return
    
    # 4. Verificar implementación de IndividualRotation
    print("\n3️⃣ Verificando clase IndividualRotation...")
    try:
        # Crear componente directamente
        rot_component = IndividualRotation(speed_x=0, speed_y=0, speed_z=1.0)
        print(f"   ✅ IndividualRotation creado")
        print(f"   Tiene calculate_delta: {hasattr(rot_component, 'calculate_delta')}")
        print(f"   Tiene update: {hasattr(rot_component, 'update')}")
        
        # Probar calculate_delta
        if hasattr(rot_component, 'calculate_delta'):
            try:
                delta = rot_component.calculate_delta(state, 0.0, 0.016)
                print(f"   Delta calculado: {delta}")
            except Exception as e:
                print(f"   ❌ Error en calculate_delta: {e}")
    except Exception as e:
        print(f"   ❌ Error creando IndividualRotation: {e}")
    
    # 5. Intentar configurar rotación manualmente
    print("\n4️⃣ Configurando rotación manualmente en motion_states...")
    try:
        # Añadir componente directamente
        state.motion.active_components['individual_rotation'] = IndividualRotation(
            speed_x=0, speed_y=0, speed_z=1.0  # 1 rad/s en Z
        )
        print("   ✅ Componente añadido a active_components")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 6. Simular update
    print("\n5️⃣ Simulando update...")
    print("   Posición antes: ", engine._positions[0])
    
    # Update manual del componente
    if 'individual_rotation' in state.motion.active_components:
        component = state.motion.active_components['individual_rotation']
        try:
            # Llamar update del componente
            if hasattr(component, 'update'):
                component.update(state, engine._time, 0.016)
            
            # Calcular delta
            if hasattr(component, 'calculate_delta'):
                delta = component.calculate_delta(state, engine._time, 0.016)
                if delta and hasattr(delta, 'position'):
                    engine._positions[0] += delta.position
                    print(f"   Delta aplicado: {delta.position}")
        except Exception as e:
            print(f"   ❌ Error en update: {e}")
    
    print("   Posición después:", engine._positions[0])
    
    # 7. Verificar el método set_individual_rotation
    print("\n6️⃣ Analizando set_individual_rotation...")
    import inspect
    try:
        source = inspect.getsource(engine.set_individual_rotation)
        print("   Implementación actual:")
        for i, line in enumerate(source.split('\n')[:10]):
            print(f"   {i}: {line}")
    except:
        print("   ❌ No se puede obtener el código fuente")
    
    # 8. Test con engine.update()
    print("\n7️⃣ Test con engine.update()...")
    initial = engine._positions[0].copy()
    
    # Asegurar que el componente esté activo
    if 0 in engine.motion_states:
        engine.motion_states[0].motion.active_components['individual_rotation'] = IndividualRotation(
            speed_x=0, speed_y=0, speed_z=2.0  # 2 rad/s para ver movimiento claro
        )
    
    # Simular 1 segundo
    for _ in range(60):
        engine.update()
    
    final = engine._positions[0]
    distance = np.linalg.norm(final - initial)
    
    print(f"\n   Posición inicial: {initial}")
    print(f"   Posición final: {final}")
    print(f"   Distancia: {distance:.6f}")
    
    # Conclusión
    print("\n" + "=" * 60)
    print("📊 CONCLUSIÓN:")
    if distance > 0.01:
        print("   ✅ Las rotaciones IS funcionan cuando se configuran manualmente")
        print("   ❌ Pero set_individual_rotation no las configura correctamente")
    else:
        print("   ❌ Las rotaciones IS no funcionan en absoluto")
        print("   Posible causa: El sistema de deltas no procesa IndividualRotation")

if __name__ == "__main__":
    diagnose_is_rotations()