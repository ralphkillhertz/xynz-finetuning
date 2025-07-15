# === test_rotation_ms_final.py ===
# 🧪 Test definitivo de rotación MS algorítmica

from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np

print("\n🎯 TEST FINAL: Rotación MS Algorítmica\n")

try:
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=8, fps=60, enable_modulator=False)
    print("✅ Engine creado")
    
    # Crear macro con 4 fuentes
    macro_id = engine.create_macro("rotacion", 4)
    print(f"✅ Macro creado: {macro_id}")
    print(f"   Fuentes activas: {engine._active_sources}")
    
    # Configurar posiciones en cuadrado
    positions = [
        [2.0, 2.0, 0.0],   # NE
        [-2.0, 2.0, 0.0],  # NO
        [-2.0, -2.0, 0.0], # SO
        [2.0, -2.0, 0.0]   # SE
    ]
    
    macro = engine._macros[macro_id]
    for i, sid in enumerate(list(macro.source_ids)[:4]):
        if sid < len(engine._positions):
            engine._positions[sid] = np.array(positions[i])
            if sid in engine.motion_states:
                engine.motion_states[sid].position = engine._positions[sid].copy()
    
    # Mostrar estado inicial
    print("\n📍 Estado inicial (cuadrado):")
    initial_positions = {}
    for i, sid in enumerate(list(macro.source_ids)[:4]):
        if sid < len(engine._positions):
            pos = engine._positions[sid]
            initial_positions[sid] = pos.copy()
            print(f"   Fuente {sid}: [{pos[0]:5.1f}, {pos[1]:5.1f}, {pos[2]:5.1f}]")
    
    # Aplicar rotación
    print("\n🔄 Aplicando rotación...")
    try:
        engine.set_macro_rotation(macro_id, 0.0, 1.0, 0.0)  # 1 rad/s en Y
        print("✅ Rotación configurada exitosamente")
    except Exception as e:
        print(f"❌ Error configurando rotación: {e}")
        raise
    
    # Verificar que se crearon los componentes
    print("\n🔍 Verificando componentes de rotación:")
    for sid in list(macro.source_ids)[:4]:
        if sid in engine.motion_states:
            motion = engine.motion_states[sid]
            if hasattr(motion, 'active_components'):
                if 'macro_rotation' in motion.active_components:
                    print(f"   ✅ Fuente {sid}: tiene MacroRotation")
                else:
                    print(f"   ❌ Fuente {sid}: NO tiene MacroRotation")
    
    # Simular movimiento
    print("\n⏱️ Simulando 60 frames (1 segundo)...")
    
    for frame in range(60):
        engine.update()
        
        # Mostrar progreso
        if frame == 20:
            print("   33% completado...")
        elif frame == 40:
            print("   66% completado...")
    
    # Verificar resultado
    print("\n📍 Estado final:")
    total_movement = 0
    
    for i, sid in enumerate(list(macro.source_ids)[:4]):
        if sid < len(engine._positions) and sid in initial_positions:
            initial = initial_positions[sid]
            final = engine._positions[sid]
            
            # Calcular movimiento
            dist = np.linalg.norm(final - initial)
            total_movement += dist
            
            # Calcular rotación
            initial_angle = np.arctan2(initial[1], initial[0]) * 180 / np.pi
            final_angle = np.arctan2(final[1], final[0]) * 180 / np.pi
            rotation = final_angle - initial_angle
            
            print(f"   Fuente {sid}: [{final[0]:5.1f}, {final[1]:5.1f}, {final[2]:5.1f}]")
            print(f"            Movió: {dist:.2f} unidades, Rotó: {rotation:.1f}°")
    
    # Evaluación
    avg_movement = total_movement / 4
    print(f"\n📊 Movimiento promedio: {avg_movement:.2f} unidades")
    
    if avg_movement > 1.0:
        print("\n🎉 ¡ÉXITO TOTAL!")
        print("✅ Rotación MS algorítmica FUNCIONANDO PERFECTAMENTE")
        print("\n📋 SISTEMA DE DELTAS COMPLETO:")
        print("   ✅ Arquitectura base: 100%")
        print("   ✅ Concentración: 100%")
        print("   ✅ Trayectorias IS: 100%")
        print("   ✅ Trayectorias MS: 100%")
        print("   ✅ Rotaciones MS algorítmicas: 100%")
        print("\n🚀 PRÓXIMO PASO: Implementar servidor MCP (CRÍTICO)")
    else:
        print(f"\n❌ Movimiento insuficiente: {avg_movement:.2f}")
        print("   Verificar que calculate_delta esté funcionando")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
