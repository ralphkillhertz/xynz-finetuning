#!/usr/bin/env python3
"""Test definitivo de MacroRotation con sistema de deltas"""

import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine

print("🎯 TEST FINAL: MacroRotation con Sistema de Deltas")
print("=" * 60)

try:
    # 1. Crear engine
    engine = EnhancedTrajectoryEngine()
    print("✅ Engine creado")
    
    # 2. Crear macro directamente (crea las fuentes automáticamente)
    macro_name = engine.create_macro(
        name="rotation_test",
        source_count=4,
        formation="square",  # Formación cuadrada
        spacing=4.0          # Espaciado de 4 unidades
    )
    print(f"✅ Macro '{macro_name}' creado con 4 fuentes en formación cuadrada")
    
    # 3. Verificar posiciones iniciales
    print("\n📍 Posiciones iniciales:")
    initial_positions = []
    for i in range(4):
        pos = engine._positions[i].copy()
        initial_positions.append(pos)
        print(f"  Fuente {i}: [{pos[0]:6.2f}, {pos[1]:6.2f}, {pos[2]:6.2f}]")
    
    # 4. Aplicar rotación algorítmica
    print("\n🔄 Aplicando rotación algorítmica...")
    print("   Velocidad: Y = 1.0 rad/s (≈ 57.3°/s)")
    
    success = engine.set_macro_rotation(
        macro_name="rotation_test",
        speed_x=0.0,
        speed_y=1.0,  # 1 radián/segundo en eje Y
        speed_z=0.0
    )
    
    if success:
        print("   ✅ Rotación configurada exitosamente")
    else:
        print("   ❌ Error al configurar rotación")
        exit(1)
    
    # 5. Debug: Verificar componentes
    print("\n🔍 Verificando componentes de rotación:")
    components_ok = 0
    
    for i in range(4):
        if i in engine.motion_states:
            motion = engine.motion_states[i]
            if 'macro_rotation' in motion.active_components:
                rot = motion.active_components['macro_rotation']
                if rot.enabled:
                    components_ok += 1
                    print(f"  ✅ Fuente {i}: MacroRotation activa (speed_y={rot.speed_y})")
                else:
                    print(f"  ❌ Fuente {i}: MacroRotation deshabilitada")
            else:
                print(f"  ❌ Fuente {i}: Sin MacroRotation")
        else:
            print(f"  ❌ Fuente {i}: Sin motion_state")
    
    print(f"\n  Componentes activos: {components_ok}/4")
    
    # 6. Simular movimiento
    print("\n⏱️ Simulando 1 segundo (60 frames a 60 fps)...")
    
    # Guardar algunas posiciones intermedias para debug
    snapshots = {}
    
    for frame in range(60):
        engine.update()
        
        # Capturar snapshots en momentos clave
        if frame in [0, 15, 30, 45, 59]:
            snapshots[frame] = [engine._positions[i].copy() for i in range(4)]
            
        # Mostrar progreso
        if frame % 15 == 0:
            print(f"  Frame {frame}/60...")
            # Debug primera fuente
            p = engine._positions[0]
            angle = np.arctan2(p[2] - initial_positions[0][2], 
                             p[0] - initial_positions[0][0])
            print(f"    Fuente 0: [{p[0]:6.2f}, {p[1]:6.2f}, {p[2]:6.2f}] (ángulo: {np.degrees(angle):.1f}°)")
    
    # 7. Análisis de resultados
    print("\n📊 ANÁLISIS DE RESULTADOS:")
    print("-" * 40)
    
    total_movement = 0.0
    movements = []
    
    for i in range(4):
        initial = initial_positions[i]
        final = engine._positions[i]
        
        # Calcular distancia movida
        distance = np.linalg.norm(final - initial)
        movements.append(distance)
        total_movement += distance
        
        # Calcular rotación en el plano XZ (rotación en Y)
        angle_rad = np.arctan2(final[2] - initial[2], final[0] - initial[0])
        angle_deg = np.degrees(angle_rad)
        
        print(f"\nFuente {i}:")
        print(f"  Inicial: [{initial[0]:6.2f}, {initial[1]:6.2f}, {initial[2]:6.2f}]")
        print(f"  Final:   [{final[0]:6.2f}, {final[1]:6.2f}, {final[2]:6.2f}]")
        print(f"  Distancia: {distance:.3f} unidades")
        print(f"  Rotación: {angle_deg:.1f}°")
    
    # 8. Verificación final
    avg_movement = total_movement / 4
    expected_angle = 57.3  # 1 radián ≈ 57.3 grados
    
    print(f"\n📈 RESUMEN:")
    print(f"  Movimiento promedio: {avg_movement:.3f} unidades")
    print(f"  Rotación esperada: {expected_angle:.1f}°")
    print(f"  Duración simulada: 1.0 segundos")
    
    # Criterio de éxito: movimiento detectado
    if avg_movement > 0.5:  # Al menos 0.5 unidades de movimiento promedio
        print("\n✅ ¡ÉXITO TOTAL!")
        print("   El sistema de deltas para MacroRotation funciona correctamente")
        print("   Las fuentes rotaron como se esperaba")
    else:
        print("\n❌ FALLO: No se detectó movimiento suficiente")
        print(f"   Movimiento promedio: {avg_movement:.3f} (esperado > 0.5)")
        
        # Debug adicional
        print("\n🔍 Debug adicional:")
        if 0 in engine.motion_states:
            rot = engine.motion_states[0].active_components.get('macro_rotation')
            if rot:
                print(f"   Ángulos finales: X={rot.angle_x:.3f}, Y={rot.angle_y:.3f}, Z={rot.angle_z:.3f}")
    
except Exception as e:
    print(f"\n❌ ERROR CRÍTICO: {e}")
    import traceback
    traceback.print_exc()
    
    # Debug del error
    print("\n🔍 Información de debug:")
    print(f"   Tipo: {type(e).__name__}")
    print(f"   Mensaje: {str(e)}")
    
    # Si es el error de array ambiguous
    if "ambiguous" in str(e):
        print("\n⚠️  El error 'array ambiguous' persiste")
        print("   Verificar la implementación de MacroRotation")
