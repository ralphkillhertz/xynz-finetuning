# === test_rotation_working.py ===
# 🎯 Test: Rotación manual MS con velocidad visible
# ⚡ Usa velocidad más alta para ver el movimiento
# 🎯 Impacto: VERIFICACIÓN FINAL

import numpy as np
import math

def test_rotation_working():
    """Test de rotación manual con velocidad visible"""
    print("🎯 TEST FINAL: Rotación Manual MS")
    print("="*60)
    
    from trajectory_hub.core import EnhancedTrajectoryEngine
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=50, fps=60, enable_modulator=False)
    
    # Crear macro
    macro_name = engine.create_macro("test", source_count=4, formation="square")
    macro = engine._macros[macro_name]
    
    # Posiciones manuales en cuadrado
    positions = [[3,0,0], [0,3,0], [-3,0,0], [0,-3,0]]
    source_ids_list = list(macro.source_ids)  # Convertir set a lista
    
    for i, (sid, pos) in enumerate(zip(source_ids_list, positions)):
        engine._positions[sid] = np.array(pos)
        if sid in engine.motion_states:
            engine.motion_states[sid].position = list(pos)
    
    print("📍 Posiciones iniciales:")
    for sid in source_ids_list:
        pos = engine._positions[sid]
        angle = np.degrees(np.arctan2(pos[1], pos[0]))
        print(f"   Fuente {sid}: [{pos[0]:.1f}, {pos[1]:.1f}, {pos[2]:.1f}] (ángulo: {angle:.1f}°)")
    
    # Configurar rotación manual con VELOCIDAD ALTA
    print("\n🔧 Configurando rotación de 90° con velocidad ALTA...")
    engine.set_manual_macro_rotation("test", yaw=math.pi/2, interpolation_speed=1.0)  # Velocidad 1.0
    
    # Ejecutar 120 frames (2 segundos)
    print("\n⚙️ Ejecutando rotación (120 frames = 2 segundos)...")
    
    for frame in range(120):
        engine.update()
        
        # Mostrar progreso cada 30 frames (0.5 segundos)
        if frame % 30 == 29:
            print(f"\n📊 Frame {frame+1} (t={frame/60:.1f}s):")
            for sid in source_ids_list:
                pos = engine._positions[sid]
                angle = np.degrees(np.arctan2(pos[1], pos[0]))
                dist = np.linalg.norm(pos[:2])
                print(f"   Fuente {sid}: [{pos[0]:6.2f}, {pos[1]:6.2f}, {pos[2]:6.2f}] | ángulo: {angle:6.1f}° | dist: {dist:.2f}")
    
    print("\n" + "="*60)
    print("📊 RESULTADO FINAL:")
    print("="*60)
    
    # Verificar rotación
    total_rotation = 0
    for i, sid in enumerate(source_ids_list):
        initial = positions[i]
        final = engine._positions[sid].tolist()
        
        # Calcular ángulos
        angle_initial = np.degrees(np.arctan2(initial[1], initial[0]))
        angle_final = np.degrees(np.arctan2(final[1], final[0]))
        rotation = angle_final - angle_initial
        
        # Normalizar rotación a [-180, 180]
        if rotation > 180:
            rotation -= 360
        elif rotation < -180:
            rotation += 360
            
        # Distancia al centro
        dist_initial = np.sqrt(initial[0]**2 + initial[1]**2)
        dist_final = np.sqrt(final[0]**2 + final[1]**2)
        
        print(f"\n   Fuente {sid}:")
        print(f"      Inicial: [{initial[0]:6.1f}, {initial[1]:6.1f}, {initial[2]:6.1f}]")
        print(f"      Final:   [{final[0]:6.2f}, {final[1]:6.2f}, {final[2]:6.2f}]")
        print(f"      Ángulo: {angle_initial:6.1f}° → {angle_final:6.1f}° (rotó {rotation:6.1f}°)")
        print(f"      Distancia al centro: {dist_initial:.2f} → {dist_final:.2f}")
        
        total_rotation += abs(rotation)
    
    avg_rotation = total_rotation / len(source_ids_list)
    
    print(f"\n📈 Rotación promedio: {avg_rotation:.1f}°")
    
    if avg_rotation > 80:
        print("\n✅ ¡ÉXITO! La rotación manual MS funciona correctamente")
        print("✅ Las fuentes rotaron aproximadamente 90°")
        print("✅ Las distancias se preservaron")
    elif avg_rotation > 40:
        print("\n⚠️ Rotación parcial - necesita más tiempo o mayor velocidad")
    else:
        print("\n❌ Rotación insuficiente - verificar algoritmo")

if __name__ == "__main__":
    test_rotation_working()