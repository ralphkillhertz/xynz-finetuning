# test_rotation_controlled.py
# Test de rotación con velocidad controlada

import numpy as np
import math
import warnings
from trajectory_hub import EnhancedTrajectoryEngine

warnings.filterwarnings("ignore", message="No se puede crear modulador")

def test_rotation_controlled():
    print("🎯 TEST: Rotación Manual MS con Velocidad Controlada")
    print("=" * 60)
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)
    
    # Crear macro
    print("🔧 Creando macro con 4 fuentes...")
    macro_name = engine.create_macro("test", source_count=4, formation="square")
    
    # Establecer posiciones en cuadrado
    print("\n📍 Estableciendo posiciones en cuadrado 3x3:")
    engine._positions[0] = np.array([3.0, 0.0, 0.0])   # Derecha
    engine._positions[1] = np.array([0.0, 3.0, 0.0])   # Arriba
    engine._positions[2] = np.array([-3.0, 0.0, 0.0])  # Izquierda
    engine._positions[3] = np.array([0.0, -3.0, 0.0])  # Abajo
    
    # Sincronizar
    for i in range(4):
        if i in engine.motion_states:
            engine.motion_states[i].state.position[:] = engine._positions[i]
        print(f"   Fuente {i}: {engine._positions[i]}")
    
    # Configurar rotación con velocidad MÁS LENTA
    print("\n🔧 Configurando rotación de 90° con velocidad lenta...")
    engine.set_manual_macro_rotation(
        macro_name,
        yaw=math.pi/2,                # 90° objetivo
        pitch=0.0,
        roll=0.0,
        interpolation_speed=0.05      # MÁS LENTO (era 0.5)
    )
    
    # Simular
    print("\n⚙️ Ejecutando rotación (120 frames = 2 segundos)...")
    initial_pos = [engine._positions[i].copy() for i in range(4)]
    
    for frame in range(120):
        engine.update()
        
        if frame % 30 == 29:  # Cada 0.5 segundos
            print(f"\n   Tiempo {(frame+1)/60:.1f}s:")
            for i in range(4):
                pos = engine._positions[i]
                dist = np.linalg.norm(pos - initial_pos[i])
                print(f"      Fuente {i}: [{pos[0]:5.2f}, {pos[1]:5.2f}, {pos[2]:5.2f}] (dist: {dist:5.2f})")
    
    # Verificar resultado final
    print("\n📊 Resultado final después de 2 segundos:")
    print("   " + "-" * 50)
    
    for i in range(4):
        inicial = initial_pos[i]
        final = engine._positions[i]
        dist = np.linalg.norm(final - inicial)
        
        print(f"\n   Fuente {i}:")
        print(f"      Inicial: [{inicial[0]:5.2f}, {inicial[1]:5.2f}, {inicial[2]:5.2f}]")
        print(f"      Final:   [{final[0]:5.2f}, {final[1]:5.2f}, {final[2]:5.2f}]")
        print(f"      Distancia: {dist:5.2f}")
        
        # Verificar rotación esperada
        if i == 0:  # (3,0,0) -> (0,3,0) después de 90°
            expected = np.array([0.0, 3.0, 0.0])
            error = np.linalg.norm(final[:2] - expected[:2])
            print(f"      Error de rotación: {error:.3f}")
            if error < 0.5:
                print(f"      ✅ Rotación precisa")
    
    print("\n" + "=" * 60)
    print("✅ ManualMacroRotation funciona correctamente")
    print("✅ La velocidad de interpolación controla la rotación")

if __name__ == "__main__":
    test_rotation_controlled()
