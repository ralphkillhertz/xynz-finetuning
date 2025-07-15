# === test_rotation_final_fixed.py ===
# 🎯 Test: Verificación final de rotación
# ⚡ Test completo después de fixes
# 🎯 Impacto: VERIFICACIÓN

import numpy as np
import math

def test_final_rotation():
    """Test final de rotación manual MS"""
    print("🎯 TEST FINAL: Rotación Manual MS")
    print("="*60)
    
    from trajectory_hub.core import EnhancedTrajectoryEngine
    
    engine = EnhancedTrajectoryEngine(max_sources=50, fps=60, enable_modulator=False)
    
    # Crear 4 fuentes en cuadrado
    macro_name = engine.create_macro("test", source_count=4, formation="square")
    macro = engine._macros[macro_name]
    source_ids = list(macro.source_ids)
    
    # Posiciones manuales
    positions = [[3,0,0], [0,3,0], [-3,0,0], [0,-3,0]]
    for i, (sid, pos) in enumerate(zip(source_ids, positions)):
        engine._positions[sid] = np.array(pos)
        if sid in engine.motion_states:
            engine.motion_states[sid].position = list(pos)
    
    # Desactivar otros componentes
    for sid in source_ids:
        state = engine.motion_states[sid]
        for name, comp in state.active_components.items():
            if hasattr(comp, 'enabled') and name != 'manual_macro_rotation':
                comp.enabled = False
    
    # Configurar rotación
    engine.set_manual_macro_rotation(macro_name, yaw=math.pi/2, interpolation_speed=0.5)
    
    print("📍 Configuración:")
    print("   4 fuentes en cuadrado 3x3")
    print("   Rotación objetivo: 90°")
    print("   Velocidad: 0.5")
    
    # Ejecutar 120 frames (2 segundos)
    print("\n⚙️ Ejecutando 120 frames...")
    
    for i in range(120):
        engine.update()
        
        if i % 30 == 29:
            print(f"\n📊 Frame {i+1}:")
            for j, sid in enumerate(source_ids):
                pos = engine._positions[sid]
                angle = np.degrees(np.arctan2(pos[1], pos[0]))
                dist = np.sqrt(pos[0]**2 + pos[1]**2)
                print(f"   Fuente {sid}: ángulo={angle:6.1f}° | dist={dist:.3f}")
    
    # Resultado final
    print("\n" + "="*60)
    print("📊 RESULTADO FINAL:")
    
    total_rotation = 0
    for i, sid in enumerate(source_ids):
        initial = positions[i]
        final = engine._positions[sid].tolist()
        
        angle_initial = np.degrees(np.arctan2(initial[1], initial[0]))
        angle_final = np.degrees(np.arctan2(final[1], final[0]))
        
        rotation = angle_final - angle_initial
        if rotation > 180: rotation -= 360
        elif rotation < -180: rotation += 360
        
        print(f"   Fuente {sid}: rotó {rotation:.1f}°")
        total_rotation += abs(rotation)
    
    avg_rotation = total_rotation / len(source_ids)
    print(f"\n📈 Rotación promedio: {avg_rotation:.1f}°")
    
    if avg_rotation > 80:
        print("✅ ¡ÉXITO! La rotación funciona correctamente")
    else:
        print("❌ La rotación no alcanzó el objetivo")

if __name__ == "__main__":
    test_final_rotation()