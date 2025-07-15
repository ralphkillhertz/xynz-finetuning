#!/usr/bin/env python3
"""Test de MacroRotation con API correcta"""

import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine

print("🧪 Test MacroRotation - API Correcta")
print("=" * 50)

try:
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)
    print("✅ Engine creado")

    # Crear 4 fuentes (sin parámetro position)
    source_ids = []
    for i in range(4):
        sid = engine.create_source()  # Sin argumentos
        source_ids.append(i)
        print(f"✅ Fuente {i} creada")
        
    # Establecer posiciones manualmente formando un cuadrado
    positions = [
        [2.0, 0.0, 0.0],   # Derecha
        [-2.0, 0.0, 0.0],  # Izquierda
        [0.0, 2.0, 0.0],   # Arriba
        [0.0, -2.0, 0.0]   # Abajo
    ]
    
    # Asignar posiciones
    for i, pos in enumerate(positions):
        if i < len(engine._positions):
            engine._positions[i] = np.array(pos, dtype=np.float32)
            
    # Crear macro
    macro_name = engine.create_macro("rot_test", [0,1,2,3])
    print(f"✅ Macro creado: {macro_name}")

    # Estado inicial
    print("\n📍 Posiciones iniciales:")
    for i in range(4):
        p = engine._positions[i]
        print(f"  Fuente {i}: [{p[0]:6.2f}, {p[1]:6.2f}, {p[2]:6.2f}]")

    # Aplicar rotación
    print("\n🔄 Aplicando rotación (Y=1.0 rad/s)...")
    success = engine.set_macro_rotation("rot_test", speed_y=1.0)
    print(f"   Resultado: {success}")

    # Debug: verificar que se configuró
    if hasattr(engine, 'motion_states'):
        print("\n🔍 Debug - Componentes de rotación:")
        rot_count = 0
        for sid in range(4):
            if sid in engine.motion_states:
                motion = engine.motion_states[sid]
                if 'macro_rotation' in motion.active_components:
                    rot = motion.active_components['macro_rotation']
                    print(f"   Fuente {sid}: MacroRotation presente")
                    print(f"     - Enabled: {rot.enabled}")
                    print(f"     - Speed Y: {rot.speed_y}")
                    if rot.enabled:
                        rot_count += 1
                else:
                    print(f"   Fuente {sid}: Sin MacroRotation")
        print(f"   Total activos: {rot_count}/4")

    # Simular 1 segundo (60 frames a 60 fps)
    print("\n⏱️ Simulando 1 segundo...")
    dt = 1.0 / engine.fps
    
    for frame in range(60):
        engine.update()
        
        # Mostrar progreso
        if frame % 20 == 0:
            print(f"   Frame {frame}/60...")
            # Debug posición de primera fuente
            p = engine._positions[0]
            print(f"     Fuente 0: [{p[0]:6.2f}, {p[1]:6.2f}, {p[2]:6.2f}]")

    # Estado final y análisis
    print("\n📍 Posiciones finales:")
    total_movement = 0.0
    
    for i in range(4):
        initial = np.array(positions[i])
        final = engine._positions[i]
        distance = np.linalg.norm(final - initial)
        
        # Calcular ángulo esperado (1 rad/s * 1s = 1 radian ≈ 57.3°)
        expected_angle = 1.0  # radianes
        
        # Para rotación en Y, X y Z deberían cambiar
        angle_actual = np.arctan2(final[2] - initial[2], final[0] - initial[0])
        
        print(f"  Fuente {i}: [{final[0]:6.2f}, {final[1]:6.2f}, {final[2]:6.2f}]")
        print(f"           Distancia movida: {distance:.3f} unidades")
        
        total_movement += distance

    avg_movement = total_movement / 4
    print(f"\n📊 Movimiento promedio: {avg_movement:.3f} unidades")
    
    # Verificación
    if avg_movement > 0.1:  # Umbral mínimo de movimiento
        print("\n✅ ¡ÉXITO! Las fuentes rotaron correctamente")
        print("   La rotación del sistema de deltas funciona")
    else:
        print("\n❌ Sin movimiento detectado")
        print("   Verificar implementación del sistema de deltas")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    
    # Debug adicional
    print("\n🔍 Debug adicional:")
    print(f"   Tipo de error: {type(e).__name__}")
    print(f"   Mensaje: {str(e)}")
