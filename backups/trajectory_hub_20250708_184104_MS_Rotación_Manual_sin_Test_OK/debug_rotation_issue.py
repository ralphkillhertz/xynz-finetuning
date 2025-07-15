# debug_rotation_issue.py
# Debug profundo del problema de rotación

import numpy as np
import math
import warnings
from trajectory_hub import EnhancedTrajectoryEngine

warnings.filterwarnings("ignore", message="No se puede crear modulador")

def debug_rotation():
    print("🔍 DEBUG: Problema de Rotación Manual")
    print("=" * 60)
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)
    
    # Crear macro
    print("1️⃣ Creando macro con 4 fuentes...")
    macro_name = engine.create_macro("debug", source_count=4, formation="square")
    
    # Establecer posiciones simples
    print("\n2️⃣ Estableciendo posiciones iniciales:")
    positions = [
        np.array([2.0, 0.0, 0.0]),   # Fuente 0: derecha
        np.array([0.0, 2.0, 0.0]),   # Fuente 1: arriba
        np.array([-2.0, 0.0, 0.0]),  # Fuente 2: izquierda
        np.array([0.0, -2.0, 0.0])   # Fuente 3: abajo
    ]
    
    for i, pos in enumerate(positions):
        engine._positions[i] = pos.copy()
        if i in engine.motion_states:
            engine.motion_states[i].state.position[:] = pos
        print(f"   Fuente {i}: {pos}")
    
    # Calcular centro esperado
    center = np.mean(positions, axis=0)
    print(f"\n   Centro calculado: {center}")
    
    # Configurar rotación
    print("\n3️⃣ Configurando rotación manual...")
    engine.set_manual_macro_rotation(
        macro_name,
        yaw=math.pi/2,                # 90°
        pitch=0.0,
        roll=0.0,
        interpolation_speed=0.1       # Velocidad moderada
    )
    
    # Verificar qué componente se creó
    print("\n4️⃣ Verificando componentes de rotación:")
    for i in range(4):
        if i in engine.motion_states:
            motion = engine.motion_states[i]
            print(f"\n   Fuente {i}:")
            print(f"      Components: {list(motion.active_components.keys())}")
            
            if 'manual_macro_rotation' in motion.active_components:
                rot_comp = motion.active_components['manual_macro_rotation']
                print(f"      ✅ Tiene manual_macro_rotation")
                print(f"      - enabled: {rot_comp.enabled}")
                print(f"      - target_yaw: {rot_comp.target_yaw}")
                print(f"      - center: {rot_comp.center}")
                
                # Test manual de calculate_delta
                state = motion.state
                delta = rot_comp.calculate_delta(state, 0.0, 1/60)
                print(f"      - Delta calculado: {delta.position}")
                print(f"      - Magnitud delta: {np.linalg.norm(delta.position):.4f}")
            else:
                print(f"      ❌ NO tiene manual_macro_rotation")
    
    # Ejecutar solo 1 frame y ver qué pasa
    print("\n5️⃣ Ejecutando 1 solo frame:")
    initial_positions = [engine._positions[i].copy() for i in range(4)]
    
    engine.update()
    
    print("\n   Cambios después de 1 frame:")
    for i in range(4):
        initial = initial_positions[i]
        final = engine._positions[i]
        change = final - initial
        dist = np.linalg.norm(change)
        
        print(f"\n   Fuente {i}:")
        print(f"      Inicial: {initial}")
        print(f"      Final:   {final}")
        print(f"      Cambio:  {change}")
        print(f"      Distancia: {dist:.4f}")
        
        if dist > 0.001:
            print(f"      ✅ Se movió")
        else:
            print(f"      ❌ NO se movió")
    
    # Verificar si es realmente una rotación
    print("\n6️⃣ Análisis de rotación:")
    
    # En una rotación real alrededor del origen:
    # - Todas las fuentes deberían moverse (excepto las del centro)
    # - La distancia al centro debería mantenerse constante
    # - El ángulo debería cambiar uniformemente
    
    for i in range(4):
        initial = initial_positions[i]
        final = engine._positions[i]
        
        # Distancia al centro
        dist_initial = np.linalg.norm(initial - center)
        dist_final = np.linalg.norm(final - center)
        
        print(f"\n   Fuente {i}:")
        print(f"      Distancia al centro inicial: {dist_initial:.4f}")
        print(f"      Distancia al centro final:   {dist_final:.4f}")
        print(f"      Cambio en distancia: {abs(dist_final - dist_initial):.4f}")
        
        if abs(dist_final - dist_initial) < 0.01:
            print(f"      ✅ Distancia al centro preservada")
        else:
            print(f"      ❌ Distancia al centro NO preservada")

if __name__ == "__main__":
    debug_rotation()
    
    print("\n💡 Si algunas fuentes no se mueven, hay un problema en la asignación de componentes")
    print("💡 Si las distancias cambian mucho, no es una rotación real")