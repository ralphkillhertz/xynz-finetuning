#!/usr/bin/env python3
"""Test final que debería funcionar"""

import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine

print("🎯 TEST FINAL MacroRotation")
print("=" * 50)

# Crear engine y macro
engine = EnhancedTrajectoryEngine()
macro_name = engine.create_macro("test", source_count=4, formation="square", spacing=4.0)
print(f"✅ Macro creado: {macro_name}")

# Establecer posiciones
positions = [[4,0,0], [0,4,0], [-4,0,0], [0,-4,0]]
for i, pos in enumerate(positions):
    engine._positions[i] = np.array(pos, dtype=np.float32)

print("\n📍 Posiciones iniciales:")
for i in range(4):
    p = engine._positions[i]
    print(f"  F{i}: [{p[0]:5.1f}, {p[1]:5.1f}, {p[2]:5.1f}]")

# Aplicar rotación
print("\n🔄 Aplicando rotación...")
try:
    success = engine.set_macro_rotation(macro_name, speed_y=1.0)
    print(f"  Resultado: {success}")
    
    # Simular
    if success:
        print("\n⏱️ Simulando 30 frames...")
        for i in range(30):
            engine.update()
            
        print("\n📍 Posiciones finales:")
        for i in range(4):
            p = engine._positions[i]
            print(f"  F{i}: [{p[0]:5.1f}, {p[1]:5.1f}, {p[2]:5.1f}]")
            
        # Verificar movimiento
        moved = any(abs(engine._positions[i][2]) > 0.1 for i in range(4))
        print(f"\n{'✅ ÉXITO' if moved else '❌ Sin movimiento'}")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    
    # Debug del error
    if "set_rotation" in str(e):
        print("\n🔍 Debug: El problema está en set_macro_rotation del engine")
        print("   Verificar que MacroRotation esté importada correctamente")
