#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
import numpy as np

print("🔍 DIAGNÓSTICO STEP()\n")

engine = EnhancedTrajectoryEngine(max_sources=4, fps=60)

# Verificar que step existe
print(f"1. ¿step() existe? {hasattr(engine, 'step')}")

# Crear macro
macro_id = engine.create_macro("test", source_count=2, formation="line", spacing=4.0)
print(f"\n2. Macro creado: {macro_id}")
print(f"   _macros: {list(engine._macros.keys())}")

# Configurar concentración
engine.set_macro_concentration(macro_id, 0.5)

# Verificar configuración
if macro_id in engine._macros:
    macro = engine._macros[macro_id]
    print(f"\n3. Macro configurado:")
    print(f"   concentration_factor: {getattr(macro, 'concentration_factor', 'NO EXISTE')}")
    print(f"   source_ids: {getattr(macro, 'source_ids', 'NO EXISTE')}")

# Debug step manualmente
print(f"\n4. Debug manual de step():")

# Copiar lógica de step para debug
for mid, m in engine._macros.items():
    print(f"\n   Procesando macro: {mid}")
    factor = getattr(m, 'concentration_factor', 0)
    print(f"   - factor: {factor}")
    
    if factor > 0 and hasattr(m, 'source_ids'):
        positions = []
        for sid in m.source_ids:
            if sid < engine.max_sources:
                pos = engine._positions[sid].copy()
                positions.append(pos)
                print(f"   - Fuente {sid}: {pos}")
        
        if len(positions) > 1:
            center = np.mean(positions, axis=0)
            print(f"   - Centro: {center}")
            
            for i, sid in enumerate(m.source_ids):
                current_pos = positions[i]
                direction = center - current_pos
                new_pos = current_pos + (direction * factor * 0.016 * 10.0)
                print(f"   - Fuente {sid} nueva pos calculada: {new_pos}")

# Llamar step real
print(f"\n5. Llamando engine.step()...")
result = engine.step()
print(f"   Resultado: {type(result)}")

print(f"\n6. Posiciones después:")
for i in range(2):
    print(f"   Fuente {i}: {engine._positions[i]}")
