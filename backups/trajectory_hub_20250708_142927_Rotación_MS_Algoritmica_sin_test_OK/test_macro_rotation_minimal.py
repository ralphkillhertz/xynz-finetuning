# === test_macro_rotation_minimal.py ===
# 🎯 Test: Versión mínima que sabemos que funciona
# ⚡ Reproducir exactamente el diagnóstico exitoso

import numpy as np
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trajectory_hub import EnhancedTrajectoryEngine

def test_rotation_minimal():
    """Test mínimo basado en el diagnóstico exitoso"""
    
    print("🎯 TEST MÍNIMO - MacroRotation")
    print("=" * 60)
    
    # Setup EXACTO del diagnóstico que funcionó
    engine = EnhancedTrajectoryEngine(max_sources=2, fps=60)
    engine.create_source(0, "test_0")
    engine._positions[0] = np.array([10.0, 0.0, 0.0])
    
    macro_name = engine.create_macro("test", source_count=1)
    engine.set_macro_rotation(macro_name, center=[0,0,0], speed_x=0, speed_y=3, speed_z=0)
    
    print("✅ Setup: 1 fuente rotando a 3 rad/s")
    
    # Posición inicial
    pos_inicial = engine._positions[0].copy()
    print(f"\n📍 Posición inicial: {pos_inicial}")
    
    # IMPORTANTE: Skip primer frame
    engine.update()
    print("✅ Primer frame (inicialización)")
    
    # Ahora sí, simular
    print("\n⏱️ Simulando 10 frames...")
    
    for i in range(10):
        engine.update()
        pos = engine._positions[0]
        dist = np.linalg.norm(pos - pos_inicial)
        angle = np.arctan2(pos[2], pos[0])
        
        if i % 3 == 0:
            print(f"  Frame {i+1}: Pos=[{pos[0]:6.2f}, {pos[2]:6.2f}] Ángulo={np.degrees(angle):6.1f}°")
    
    # Resultado final
    pos_final = engine._positions[0]
    dist_total = np.linalg.norm(pos_final - pos_inicial)
    
    print(f"\n📊 RESULTADO:")
    print(f"  Inicial: {pos_inicial}")
    print(f"  Final:   {pos_final}")
    print(f"  Distancia: {dist_total:.3f}")
    
    success = dist_total > 1.0  # Al menos 1 unidad de movimiento
    
    if success:
        print("\n✅ ÉXITO: La rotación funciona!")
        
        # Ahora probar con múltiples fuentes
        print("\n" + "="*60)
        print("🔍 PROBANDO CON 4 FUENTES...")
        
        engine2 = EnhancedTrajectoryEngine(max_sources=5, fps=60)
        
        # Crear fuentes una por una
        for i in range(4):
            result = engine2.create_source(i, f"test_{i}")
            print(f"  Fuente {i}: creada = {result is not None}")
        
        # Ver motion_states
        print(f"\n  motion_states: {list(engine2.motion_states.keys())}")
        
        # Crear macro
        macro2 = engine2.create_macro("test2", source_count=4)
        print(f"  Macro creado: {macro2}")
        
        # Ver si las fuentes están en el macro
        if macro2 in engine2._macros:
            macro_obj = engine2._macros[macro2]
            print(f"  Fuentes en macro: {list(macro_obj.source_ids)}")
    else:
        print("\n❌ No hay rotación")
    
    return success

if __name__ == "__main__":
    success = test_rotation_minimal()
    
    if success:
        print("\n💡 CONCLUSIÓN:")
        print("  MacroRotation funciona con 1 fuente")
        print("  Verificar por qué falla con múltiples fuentes")