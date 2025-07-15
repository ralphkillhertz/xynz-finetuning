# === test_manual_simple.py ===
# Test simple de rotación manual

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np
import math

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=10, fps=60, enable_modulator=False)
print("✅ Engine creado")

# Crear macro - empezar con posiciones manuales
macro_name = engine.create_macro("test", source_count=4)
macro = engine._macros[macro_name]
source_ids = list(macro.source_ids)

# Establecer posiciones iniciales manualmente en un cuadrado
positions = [
    np.array([2.0, 2.0, 0.0]),   # Superior derecha
    np.array([-2.0, 2.0, 0.0]),  # Superior izquierda
    np.array([-2.0, -2.0, 0.0]), # Inferior izquierda
    np.array([2.0, -2.0, 0.0])   # Inferior derecha
]

for sid, pos in zip(source_ids, positions):
    engine._positions[sid] = pos
    print(f"Fuente {sid}: posición inicial = {pos}")

# Configurar rotación manual
print("\n🔧 Configurando rotación manual...")
success = engine.set_manual_macro_rotation(
    macro_name,
    yaw=math.pi/4,  # 45 grados
    interpolation_speed=0.1
)

if success:
    print("✅ Rotación configurada")
    
    # Ejecutar algunos updates
    print("\n🔄 Ejecutando rotación...")
    for i in range(20):
        engine.update()
        
        if i % 5 == 0:
            pos = engine._positions[source_ids[0]]
            print(f"   Update {i}: Primera fuente en {pos}")
    
    # Verificar resultado
    print("\n📊 Posiciones finales:")
    for sid in source_ids:
        print(f"   Fuente {sid}: {engine._positions[sid]}")
else:
    print("❌ Error configurando rotación")
