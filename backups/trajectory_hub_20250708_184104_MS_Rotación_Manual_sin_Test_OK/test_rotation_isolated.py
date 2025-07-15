# === test_rotation_isolated.py ===
# 🎯 Test: Rotación manual MS aislada
# ⚡ Desactiva otros componentes para probar solo rotación
# 🎯 Impacto: VERIFICACIÓN AISLADA

import numpy as np
import math

def test_isolated_rotation():
    """Test de rotación manual sin interferencias"""
    print("🎯 TEST AISLADO: Rotación Manual MS")
    print("="*60)
    
    from trajectory_hub.core import EnhancedTrajectoryEngine
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=50, fps=60, enable_modulator=False)
    
    # Crear macro
    macro_name = engine.create_macro("test", source_count=4, formation="square")
    macro = engine._macros[macro_name]
    source_ids_list = list(macro.source_ids)
    
    # Posiciones manuales
    positions = [[3,0,0], [0,3,0], [-3,0,0], [0,-3,0]]
    for i, (sid, pos) in enumerate(zip(source_ids_list, positions)):
        engine._positions[sid] = np.array(pos)
        if sid in engine.motion_states:
            engine.motion_states[sid].position = list(pos)
    
    # IMPORTANTE: Desactivar macro_trajectory si existe
    print("\n🔧 Desactivando otros componentes...")
    for sid in source_ids_list:
        state = engine.motion_states[sid]
        if 'macro_trajectory' in state.active_components:
            comp = state.active_components['macro_trajectory']
            comp.enabled = False
            print(f"   ✅ macro_trajectory desactivado para fuente {sid}")
    
    # Configurar rotación manual
    print("\n🔧 Configurando rotación manual...")
    engine.set_manual_macro_rotation(macro_name, yaw=math.pi/2, interpolation_speed=1.0)
    
    print("\n📍 Estado inicial:")
    for sid in source_ids_list:
        pos = engine._positions[sid]
        print(f"   Fuente {sid}: [{pos[0]:.3f}, {pos[1]:.3f}, {pos[2]:.3f}]")
    
    # Ejecutar 60 frames (1 segundo)
    print("\n⚙️ Ejecutando 60 frames...")
    for frame in range(60):
        engine.update()
        
        # Mostrar cada 15 frames
        if frame % 15 == 14:
            print(f"\n📊 Frame {frame+1}:")
            for sid in source_ids_list:
                pos = engine._positions[sid]
                angle = np.degrees(np.arctan2(pos[1], pos[0]))
                print(f"   Fuente {sid}: [{pos[0]:6.3f}, {pos[1]:6.3f}, {pos[2]:6.3f}] | ángulo: {angle:7.2f}°")
    
    # Resultado final
    print("\n" + "="*60)
    print("📊 RESULTADO FINAL:")
    for i, sid in enumerate(source_ids_list):
        initial = positions[i]
        final = engine._positions[sid]
        
        angle_initial = np.degrees(np.arctan2(initial[1], initial[0]))
        angle_final = np.degrees(np.arctan2(final[1], final[0]))
        rotation = angle_final - angle_initial
        
        # Normalizar
        if rotation > 180:
            rotation -= 360
        elif rotation < -180:
            rotation += 360
        
        print(f"\n   Fuente {sid}: rotó {rotation:.1f}° (de {angle_initial:.1f}° a {angle_final:.1f}°)")
    
    # Verificar componentes activos finales
    print("\n🔍 Componentes activos:")
    state = engine.motion_states[source_ids_list[0]]
    for name, comp in state.active_components.items():
        print(f"   {name}: enabled={getattr(comp, 'enabled', '?')}")

if __name__ == "__main__":
    test_isolated_rotation()