#!/usr/bin/env python3
"""
🧪 TEST SIMPLE DE CONCENTRACIÓN
"""

import os
import sys
import numpy as np

current_dir = os.getcwd()
if 'trajectory_hub' in current_dir:
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

os.environ['DISABLE_OSC'] = '1'

print("🧪 TEST SIMPLE DE CONCENTRACIÓN")
print("=" * 50)

try:
    from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=4, fps=60)
    
    # Crear macro
    macro_id = engine.create_macro("test", source_count=4, formation="grid", spacing=6.0)
    print(f"✅ Macro creado: {macro_id}")
    
    # Obtener posiciones iniciales
    positions_before = []
    for i in range(4):
        pos = engine._positions[i].copy()
        positions_before.append(pos)
        print(f"   Fuente {i}: {pos}")
    
    # Calcular centro y dispersión inicial
    center = np.mean(positions_before, axis=0)
    dispersion_before = np.mean([np.linalg.norm(p - center) for p in positions_before])
    print(f"\nCentro: {center}")
    print(f"Dispersión inicial: {dispersion_before:.2f}")
    
    # Aplicar concentración
    print("\n🎯 Aplicando concentración (factor=0.8)...")
    engine.set_macro_concentration(macro_id, 0.8)
    
    # Ejecutar simulación
    print("\n🔄 Ejecutando 60 frames...")
    time = 0.0
    dt = 1.0 / 60.0
    
    for frame in range(60):
        # Llamar update con time y dt
        result = engine.update(dt)
        time += dt
        
        # Mostrar progreso cada 20 frames
        if frame % 20 == 0:
            pos = engine._positions[0]
            dist_to_center = np.linalg.norm(pos - center)
            print(f"   Frame {frame}: distancia al centro = {dist_to_center:.2f}")
    
    # Verificar resultado
    print("\n📊 RESULTADO:")
    positions_after = []
    for i in range(4):
        pos = engine._positions[i]
        positions_after.append(pos)
        print(f"   Fuente {i}: {pos}")
    
    # Calcular dispersión final
    center_after = np.mean(positions_after, axis=0)
    dispersion_after = np.mean([np.linalg.norm(p - center_after) for p in positions_after])
    
    print(f"\nDispersión final: {dispersion_after:.2f}")
    reduction = (dispersion_before - dispersion_after) / dispersion_before * 100
    print(f"Reducción: {reduction:.1f}%")
    
    # Verificar movimiento
    total_movement = sum(np.linalg.norm(p1 - p2) for p1, p2 in zip(positions_before, positions_after))
    
    if reduction > 10 and total_movement > 0.1:
        print("\n✅ ¡CONCENTRACIÓN FUNCIONA!")
    else:
        print("\n❌ La concentración no está funcionando")
        print(f"   Movimiento total: {total_movement:.4f}")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
