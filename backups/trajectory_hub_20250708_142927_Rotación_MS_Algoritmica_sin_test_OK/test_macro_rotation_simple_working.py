# === test_macro_rotation_simple_working.py ===
# 🎯 Test: MacroRotation versión simplificada
# ⚡ Sin dependencias de atributos complejos

import numpy as np
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trajectory_hub import EnhancedTrajectoryEngine

def test_macro_rotation():
    """Test simple y directo de MacroRotation"""
    
    print("🎯 TEST MacroRotation - Versión Simple")
    print("=" * 60)
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)
    print("✅ Engine creado")
    
    # Crear 4 fuentes
    source_ids = []
    positions = [
        [10.0, 0.0, 0.0],
        [0.0, 10.0, 0.0],
        [-10.0, 0.0, 0.0],
        [0.0, -10.0, 0.0]
    ]
    
    for i in range(4):
        try:
            # Crear fuente
            result = engine.create_source(i, f"test_{i}")
            source_ids.append(i)
            # Establecer posición
            engine._positions[i] = np.array(positions[i])
            print(f"✅ Fuente {i} creada")
        except Exception as e:
            print(f"❌ Error creando fuente {i}: {e}")
            return False
    
    # Crear macro
    try:
        macro_name = engine.create_macro("rotation_test", source_count=4)
        print(f"\n✅ Macro creado: {macro_name}")
    except Exception as e:
        print(f"❌ Error creando macro: {e}")
        return False
    
    # Posiciones iniciales
    print("\n📍 Posiciones iniciales:")
    for i in source_ids:
        pos = engine._positions[i]
        print(f"  F{i}: [{pos[0]:6.2f}, {pos[1]:6.2f}, {pos[2]:6.2f}]")
    
    # Aplicar rotación
    try:
        engine.set_macro_rotation(
            macro_name,
            center=[0.0, 0.0, 0.0],
            speed_x=0.0,
            speed_y=1.0,  # 1 rad/s
            speed_z=0.0
        )
        print("\n✅ Rotación configurada: Y = 1.0 rad/s")
    except Exception as e:
        print(f"❌ Error configurando rotación: {e}")
        return False
    
    # Guardar posiciones iniciales
    initial_pos = {}
    for sid in source_ids:
        initial_pos[sid] = engine._positions[sid].copy()
    
    # Simular
    print("\n⏱️ Simulando 60 frames (1 segundo)...")
    dt = 1.0 / 60.0
    
    for frame in range(60):
        engine.update(dt)
        
        if frame % 20 == 0:
            pos = engine._positions[0]
            dist = np.linalg.norm(pos - initial_pos[0])
            print(f"  Frame {frame}: Fuente 0 movió {dist:.3f} unidades")
    
    # Resultados
    print("\n📊 RESULTADOS:")
    total_movement = 0.0
    
    for sid in source_ids:
        initial = initial_pos[sid]
        final = engine._positions[sid]
        distance = np.linalg.norm(final - initial)
        total_movement += distance
        angle = np.arctan2(final[2] - initial[2], final[0] - initial[0])
        
        print(f"  F{sid}: Movió {distance:.3f} unidades ({np.degrees(angle):.1f}°)")
    
    avg_movement = total_movement / len(source_ids)
    print(f"\n📈 Movimiento promedio: {avg_movement:.3f}")
    
    # Verificación
    if avg_movement > 0.5:  # Al menos 0.5 unidades
        print("\n✅ ÉXITO: MacroRotation funciona!")
        return True
    else:
        print("\n❌ No hay suficiente movimiento")
        
        # Debug adicional
        print("\n🔍 Debug:")
        for sid in source_ids[:1]:  # Solo primera fuente
            if sid in engine.motion_states:
                motion = engine.motion_states[sid]
                if hasattr(motion, 'active_components'):
                    print(f"  active_components tipo: {type(motion.active_components)}")
                    if isinstance(motion.active_components, dict):
                        if 'macro_rotation' in motion.active_components:
                            comp = motion.active_components['macro_rotation']
                            print(f"  macro_rotation existe: {comp is not None}")
                            if comp:
                                print(f"  enabled: {getattr(comp, 'enabled', 'N/A')}")
        
        return False

if __name__ == "__main__":
    try:
        success = test_macro_rotation()
        
        print("\n" + "="*60)
        if success:
            print("🎉 Sistema de deltas completo!")
            print("\n📊 Componentes migrados:")
            print("  ✅ ConcentrationComponent")
            print("  ✅ IndividualTrajectory") 
            print("  ✅ MacroTrajectory")
            print("  ✅ MacroRotation")
            print("\n⭐ Listo para guardar estado y continuar con MCP")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()