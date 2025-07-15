# === test_multiple_updates.py ===
# 🔍 Test: Ver qué pasa con múltiples updates
# ⚡ Identifica si el problema es acumulativo
# 🎯 Impacto: DIAGNÓSTICO CRÍTICO

import numpy as np
import math

def test_multiple_updates():
    """Test con múltiples updates para ver el patrón"""
    print("🔍 TEST: Múltiples Updates Consecutivos")
    print("="*60)
    
    from trajectory_hub.core import EnhancedTrajectoryEngine
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=50, fps=60, enable_modulator=False)
    
    # Crear una sola fuente
    motion = engine.create_source(0)
    engine._positions[0] = np.array([3.0, 0.0, 0.0])
    if 0 in engine.motion_states:
        engine.motion_states[0].position = [3.0, 0.0, 0.0]
    
    # Crear macro
    macro_name = engine.create_macro("test", source_count=1)
    
    # Desactivar todo excepto rotación
    state = engine.motion_states[0]
    for name, comp in state.active_components.items():
        if hasattr(comp, 'enabled') and name != 'manual_macro_rotation':
            comp.enabled = False
    
    # Configurar rotación
    engine.set_manual_macro_rotation(macro_name, yaw=math.pi/2, interpolation_speed=1.0)
    
    print("📍 Posición inicial: [3.0, 0.0, 0.0]")
    print("🎯 Objetivo: rotar 90° alrededor del origen")
    print("\n⚙️ Ejecutando 10 updates...")
    
    # Tracking
    positions = []
    deltas = []
    
    for i in range(10):
        pos_before = engine._positions[0].copy()
        
        # Update
        engine.update()
        
        pos_after = engine._positions[0]
        delta = pos_after - pos_before
        
        positions.append(pos_after.copy())
        deltas.append(delta)
        
        # Calcular ángulo y distancia
        angle = np.degrees(np.arctan2(pos_after[1], pos_after[0]))
        distance = np.sqrt(pos_after[0]**2 + pos_after[1]**2)
        
        print(f"\n   Update {i+1}:")
        print(f"      Posición: [{pos_after[0]:7.4f}, {pos_after[1]:7.4f}, {pos_after[2]:7.4f}]")
        print(f"      Delta:    [{delta[0]:7.4f}, {delta[1]:7.4f}, {delta[2]:7.4f}]")
        print(f"      Ángulo: {angle:6.2f}°  |  Distancia: {distance:.4f}")
    
    # Análisis
    print("\n" + "="*60)
    print("📊 ANÁLISIS:")
    
    # Ver si los deltas son consistentes
    print("\n1️⃣ Consistencia de deltas:")
    delta_x = [d[0] for d in deltas]
    delta_y = [d[1] for d in deltas]
    
    if all(abs(dx - 0.1) < 0.001 for dx in delta_x):
        print("   ❌ Delta X constante ~0.1 - Movimiento LINEAL")
    elif all(abs(dx) < 0.01 for dx in delta_x):
        print("   ✅ Delta X pequeño y variable - Rotación")
    else:
        print(f"   ⚠️ Delta X variable: min={min(delta_x):.4f}, max={max(delta_x):.4f}")
    
    # Ver si es rotación o traslación
    final_pos = positions[-1]
    initial_angle = 0.0
    final_angle = np.degrees(np.arctan2(final_pos[1], final_pos[0]))
    
    print(f"\n2️⃣ Tipo de movimiento:")
    print(f"   Ángulo: {initial_angle:.1f}° → {final_angle:.1f}°")
    print(f"   Posición X: 3.0 → {final_pos[0]:.2f}")
    
    if final_pos[0] > 5.0:
        print("   ❌ TRASLACIÓN LINEAL detectada")
    elif abs(final_angle) > 10:
        print("   ✅ ROTACIÓN detectada")
    else:
        print("   ⚠️ Movimiento ambiguo")

if __name__ == "__main__":
    test_multiple_updates()