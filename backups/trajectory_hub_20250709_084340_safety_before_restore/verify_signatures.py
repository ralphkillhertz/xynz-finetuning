# === verify_signatures.py ===
# 🔍 Verificar firmas de update
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub.core import EnhancedTrajectoryEngine

# Test simple
engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)
macro = engine.create_macro("test", 2, formation='line')

# Aplicar varios componentes
engine.set_macro_concentration(macro, 0.5)
engine.set_individual_trajectory(macro, 0, 'circle', {'radius': 2.0})

try:
    # Múltiples updates para verificar
    for i in range(5):
        engine.update()
    
    print("✅ Sistema funcionando correctamente")
    print(f"   Posición fuente 0: {engine._positions[0]}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
