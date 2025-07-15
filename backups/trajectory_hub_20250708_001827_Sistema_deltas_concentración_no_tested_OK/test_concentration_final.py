# === test_concentration_final.py ===
# 🧪 Test final con todo restaurado
# ⚡ Este DEBE funcionar

import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine

print("🎉 TEST FINAL - SISTEMA COMPLETO")
print("="*60)

try:
    # Setup
    engine = EnhancedTrajectoryEngine()
    macro = engine.create_macro("test", source_count=3)
    
    # Posiciones iniciales en círculo
    for i in range(3):
        angle = i * 2 * np.pi / 3
        engine._positions[i] = np.array([10 * np.cos(angle), 10 * np.sin(angle), 0])
    
    print("📍 Posiciones iniciales:")
    for i in range(3):
        pos = engine._positions[i]
        dist = np.linalg.norm(pos)
        print(f"   Source {i}: {pos} (dist={dist:.2f})")
    
    # Aplicar concentración
    print("\n🎯 Aplicando concentración (factor=0.5)...")
    engine.set_macro_concentration(macro, factor=0.5)
    
    # Actualizar y monitorear
    print("\n🔄 Actualizando...")
    distances = []
    for frame in range(30):
        engine.update()
        
        # Medir distancias cada 10 frames
        if frame % 10 == 9:
            avg_dist = np.mean([np.linalg.norm(engine._positions[i]) for i in range(3)])
            distances.append(avg_dist)
            print(f"   Frame {frame+1}: distancia promedio = {avg_dist:.2f}")
    
    # Resultado final
    print("\n📊 RESULTADO FINAL:")
    for i in range(3):
        pos = engine._positions[i]
        dist = np.linalg.norm(pos)
        print(f"   Source {i}: {pos} (dist={dist:.2f})")
    
    # Verificar si se movieron
    initial_dist = 10.0
    final_dist = distances[-1] if distances else 10.0
    
    if final_dist < initial_dist - 0.1:
        print(f"\n🎉 ¡ÉXITO! Las fuentes se concentraron")
        print(f"   Distancia inicial: {initial_dist:.2f}")
        print(f"   Distancia final: {final_dist:.2f}")
        print(f"   Reducción: {((initial_dist - final_dist) / initial_dist * 100):.1f}%")
        print("\n✅ EL SISTEMA DE DELTAS FUNCIONA CORRECTAMENTE")
    else:
        print("\n❌ Las fuentes NO se movieron")
        print("\n🔍 Verificando componentes...")
        motion = engine.motion_states[0]
        print(f"   active_components: {motion.active_components}")
        if motion.active_components:
            comp = motion.active_components[0]
            print(f"   Tipo: {type(comp).__name__}")
            if hasattr(comp, 'calculate_delta'):
                delta = comp.calculate_delta(motion.state, 0, 0.016)
                print(f"   Delta calculado: {delta}")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()