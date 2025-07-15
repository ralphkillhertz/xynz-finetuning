# === diagnose_constructor.py ===
# Diagnostica los parámetros correctos del constructor

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub import EnhancedTrajectoryEngine
import inspect

# Ver la firma del constructor
sig = inspect.signature(EnhancedTrajectoryEngine.__init__)
print("🔍 Parámetros del constructor:")
print(f"   {sig}")

# Intentar crear con parámetros básicos
try:
    engine = EnhancedTrajectoryEngine()
    print("\n✅ Constructor sin parámetros funciona")
except Exception as e:
    print(f"\n❌ Error sin parámetros: {e}")

# Probar con max_sources
try:
    engine = EnhancedTrajectoryEngine(max_sources=10)
    print("✅ Constructor con max_sources=10 funciona")
except Exception as e:
    print(f"❌ Error con max_sources: {e}")

# Probar con fps
try:
    engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)
    print("✅ Constructor con max_sources=10, fps=60 funciona")
except Exception as e:
    print(f"❌ Error con max_sources y fps: {e}")
