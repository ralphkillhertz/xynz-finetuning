# === verify_formations.py ===
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)

# Test diferentes formaciones
formations = ["circle", "line", "square", "grid", "spiral"]

for formation in formations:
    print(f"\n🧪 Testing {formation} formation:")
    
    # Crear macro
    macro_name = engine.create_macro(f"test_{formation}", 
                                   source_count=4, 
                                   formation=formation,
                                   spacing=2.0)
    
    # Verificar posiciones
    macro = engine._macros[macro_name]
    
    all_zero = True
    for sid in list(macro.source_ids):
        pos = engine._positions[sid]
        if not np.allclose(pos, [0, 0, 0]):
            all_zero = False
        print(f"   Fuente {sid}: {pos}")
    
    if all_zero:
        print(f"   ⚠️ Todas las posiciones son [0,0,0]")
    else:
        print(f"   ✅ Formación correcta")
