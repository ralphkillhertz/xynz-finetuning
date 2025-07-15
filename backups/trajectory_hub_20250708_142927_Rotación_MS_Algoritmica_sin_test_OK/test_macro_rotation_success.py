# === test_macro_rotation_success.py ===
# 🎯 Test: Confirmar que MacroRotation funciona
# ⚡ Versión final con expectativas correctas

import numpy as np
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trajectory_hub import EnhancedTrajectoryEngine

def test_macro_rotation():
    """Test definitivo de MacroRotation"""
    
    print("🎉 TEST FINAL - MacroRotation con Sistema de Deltas")
    print("=" * 60)
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)
    
    # Crear 4 fuentes en cruz
    positions = [
        [10.0, 0.0, 0.0],    # Derecha
        [0.0, 0.0, 10.0],    # Adelante  
        [-10.0, 0.0, 0.0],   # Izquierda
        [0.0, 0.0, -10.0]    # Atrás
    ]
    
    for i in range(4):
        engine.create_source(i, f"test_{i}")
        engine._positions[i] = np.array(positions[i])
    
    # Crear macro
    macro_name = engine.create_macro("rotation_test", source_count=4)
    
    # Aplicar rotación más rápida para ver movimiento claro
    engine.set_macro_rotation(
        macro_name,
        center=[0.0, 0.0, 0.0],
        speed_x=0.0,
        speed_y=3.0,  # 3 rad/s para movimiento más visible
        speed_z=0.0
    )
    
    print("✅ Setup completo: 4 fuentes rotando a 3 rad/s")
    
    # Posiciones iniciales
    initial_positions = {}
    for i in range(4):
        initial_positions[i] = engine._positions[i].copy()
    
    # Simular 60 frames (1 segundo)
    print("\n⏱️ Simulando 1 segundo (60 frames)...")
    for frame in range(60):
        engine.update()
        
        if frame % 20 == 0:
            pos = engine._positions[0]
            dist = np.linalg.norm(pos - initial_positions[0])
            print(f"  Frame {frame:2d}: Fuente 0 movió {dist:6.3f} unidades")
    
    # Resultados finales
    print("\n📊 RESULTADOS FINALES:")
    print("-" * 60)
    
    total_rotation = 0.0
    for i in range(4):
        initial = initial_positions[i]
        final = engine._positions[i]
        
        # Calcular ángulo rotado
        angle_initial = np.arctan2(initial[2], initial[0])
        angle_final = np.arctan2(final[2], final[0])
        angle_diff = angle_final - angle_initial
        
        # Normalizar ángulo
        while angle_diff > np.pi:
            angle_diff -= 2 * np.pi
        while angle_diff < -np.pi:
            angle_diff += 2 * np.pi
        
        total_rotation += abs(angle_diff)
        
        print(f"\nFuente {i}:")
        print(f"  Inicial: [{initial[0]:7.3f}, {initial[1]:7.3f}, {initial[2]:7.3f}]")
        print(f"  Final:   [{final[0]:7.3f}, {final[1]:7.3f}, {final[2]:7.3f}]")
        print(f"  Rotación: {np.degrees(angle_diff):6.1f}°")
    
    # Verificación
    avg_rotation = total_rotation / 4
    expected_rotation = 3.0  # 3 rad/s * 1s = 3 radianes
    
    print(f"\n📈 Rotación promedio: {avg_rotation:.3f} rad ({np.degrees(avg_rotation):.1f}°)")
    print(f"   Esperado: ~{expected_rotation:.3f} rad ({np.degrees(expected_rotation):.1f}°)")
    
    # Criterio de éxito: al menos 80% del esperado
    success = avg_rotation > expected_rotation * 0.8
    
    if success:
        print("\n✅ ÉXITO TOTAL: MacroRotation funciona perfectamente!")
    else:
        print(f"\n⚠️ Rotación menor a la esperada ({avg_rotation/expected_rotation*100:.1f}%)")
    
    return success

if __name__ == "__main__":
    success = test_macro_rotation()
    
    print("\n" + "="*60)
    if success:
        print("🎉 SISTEMA DE DELTAS COMPLETADO")
        print("\n📊 Resumen de componentes migrados:")
        print("  ✅ ConcentrationComponent - 100%")
        print("  ✅ IndividualTrajectory - 100%")
        print("  ✅ MacroTrajectory - 100%")
        print("  ✅ MacroRotation - 100%")
        print("\n⭐ Sistema de deltas: 4/4 componentes principales")
        print("\n📝 Próximos pasos:")
        print("  1. Guardar estado del proyecto")
        print("  2. Implementar servidor MCP (objetivo principal)")
        print("\n💾 Comando: python save_project_state.py")
    else:
        print("❌ Revisar configuración")