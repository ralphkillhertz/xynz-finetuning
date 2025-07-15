import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub.core import EnhancedTrajectoryEngine

# Test rápido
engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)
macro = engine.create_macro("test", 2)
engine.set_macro_concentration(macro, 0.5)

try:
    engine.update()
    print("✅ Update funciona correctamente")
except Exception as e:
    print(f"❌ Error: {e}")
