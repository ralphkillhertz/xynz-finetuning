#!/usr/bin/env python3
"""Test de rotación con API correcta descubierta"""

import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine

print("🧪 Test MacroRotation con API Real")
print("=" * 50)

try:
    # Crear engine
    engine = EnhancedTrajectoryEngine()
    print("✅ Engine creado")
    
    # Crear 4 fuentes con la API correcta
    source_ids = []
    for i in range(4):
        # Usar source_id numérico según el diagnóstico
        result = engine.create_source(i)
        source_ids.append(i)
        print(f"✅ Fuente {i} creada: {result}")
    
    # Establecer posiciones en cuadrado
    positions = [
        [2.0, 0.0, 0.0],   # Derecha
        [-2.0, 0.0, 0.0],  # Izquierda  
        [0.0, 2.0, 0.0],   # Arriba
        [0.0, -2.0, 0.0]   # Abajo
    ]
    
    for i, pos in enumerate(positions):
        if i < len(engine._positions):
            engine._positions[i] = np.array(pos, dtype=np.float32)
    
    # Crear macro con source_ids correctos
    macro_name = engine.create_macro("rot_test", source_ids)
    print(f"\n✅ Macro creado: {macro_name}")
    
    # Mostrar posiciones iniciales
    print("\n📍 Posiciones iniciales:")
    for i in range(4):
        p = engine._positions[i]
        print(f"  Fuente {i}: [{p[0]:6.2f}, {p[1]:6.2f}, {p[2]:6.2f}]")
    
    # Aplicar rotación
    print("\n🔄 Aplicando rotación Y=1.0 rad/s...")
    
    # Verificar si el método existe
    if hasattr(engine, 'set_macro_rotation'):
        success = engine.set_macro_rotation("rot_test", speed_y=1.0)
        print(f"   Resultado: {success}")
        
        # Simular
        print("\n⏱️ Simulando 60 frames...")
        for frame in range(60):
            engine.update()
            if frame % 20 == 0:
                p0 = engine._positions[0]
                print(f"   Frame {frame}: Fuente 0 en [{p0[0]:6.2f}, {p0[1]:6.2f}, {p0[2]:6.2f}]")
        
        # Verificar movimiento
        print("\n📍 Posiciones finales:")
        moved = False
        for i in range(4):
            initial = np.array(positions[i])
            final = engine._positions[i]
            dist = np.linalg.norm(final - initial)
            print(f"  Fuente {i}: [{final[0]:6.2f}, {final[1]:6.2f}, {final[2]:6.2f}] (dist: {dist:.3f})")
            if dist > 0.1:
                moved = True
        
        print(f"\n{'✅ ÉXITO' if moved else '❌ FALLO'}: {'Rotación funciona' if moved else 'Sin movimiento'}")
        
    else:
        print("❌ set_macro_rotation no existe en el engine")
        print("   Verificar que se añadió correctamente")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
