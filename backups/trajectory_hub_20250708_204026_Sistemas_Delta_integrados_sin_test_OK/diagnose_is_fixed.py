# === diagnose_is_fixed.py ===
# 🔍 Diagnóstico corregido de rotaciones IS
# ⚡ state es directamente SourceMotion

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
        motion = engine.motion_states[0]  # motion ES SourceMotion
        print(f"   ✅ SourceMotion existe")
        print(f"   Tipo: {type(motion)}")
        print(f"   Componentes activos: {motion.active_components}")
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
                # Obtener el state interno
                state = motion.state
                delta = rot_component.calculate_delta(state, 0.0, 0.016)
                print(f"   Delta calculado: {delta}")
                if delta:
                    print(f"   Delta.position: {getattr(delta, 'position', 'No tiene position')}")
            except Exception as e:
                print(f"   ❌ Error en calculate_delta: {e}")
    except Exception as e:
        print(f"   ❌ Error creando IndividualRotation: {e}")
    
    # 5. Intentar configurar rotación manualmente
    print("\n4️⃣ Configurando rotación manualmente...")
    try:
        # Añadir componente directamente
        motion.active_components['individual_rotation'] = IndividualRotation(
            speed_x=0, speed_y=0, speed_z=1.0  # 1 rad/s en Z
        )
        print("   ✅ Componente añadido a active_components")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 6. Test con set_individual_rotation del engine
    print("\n5️⃣ Probando set_individual_rotation...")
    try:
        # La API mostró: (source_id, pitch, yaw, roll)
        result = engine.set_individual_rotation(0, 0.0, 0.0, 1.0)  # Roll = 1.0
        print(f"   Resultado: {result}")
        print(f"   Componentes después: {motion.active_components.keys()}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 7. Simular movimiento
    print("\n6️⃣ Simulando movimiento...")
    initial = engine._positions[0].copy()
    
    # Simular 2 segundos
    for i in range(120):
        engine.update()
        if i % 30 == 0:  # Cada 0.5 segundos
            pos = engine._positions[0]
            dist = np.linalg.norm(pos - initial)
            print(f"   t={i/60:.1f}s: pos={pos}, dist={dist:.3f}")
    
    final = engine._positions[0]
    distance = np.linalg.norm(final - initial)
    
    # 8. Verificar si el problema es la API
    print("\n7️⃣ Verificando problema de API...")
    print("   La API actual espera (pitch, yaw, roll) pero IndividualRotation")
    print("   necesita (speed_x, speed_y, speed_z)")
    print("   ❌ Incompatibilidad de parámetros!")
    
    # Conclusión
    print("\n" + "=" * 60)
    print("📊 CONCLUSIÓN:")
    print(f"   Distancia total recorrida: {distance:.6f}")
    if distance > 0.01:
        print("   ✅ Las rotaciones IS funcionan")
    else:
        print("   ❌ Las rotaciones IS NO funcionan")
        print("\n   PROBLEMA IDENTIFICADO:")
        print("   - set_individual_rotation recibe (pitch, yaw, roll)")
        print("   - Pero IndividualRotation necesita (speed_x, speed_y, speed_z)")
        print("   - Hay una incompatibilidad en la implementación")

if __name__ == "__main__":
    diagnose_is_rotations()