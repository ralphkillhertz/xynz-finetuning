# === test_quick.py ===
# 🚀 Test rápido post-fixes

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub.core import EnhancedTrajectoryEngine
import numpy as np

print("🧪 TEST RÁPIDO")
print("=" * 40)

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)

# Test 1: Macro con sets
print("\n1️⃣ Test macro y sets")
macro = engine.create_macro("test", 3)
print(f"   source_ids tipo: {type(macro.source_ids)}")
print(f"   source_ids: {macro.source_ids}")
sids_list = list(macro.source_ids)
print(f"   Como lista: {sids_list}")
print(f"   Primer elemento: {sids_list[0]}")

# Test 2: Rotación individual
print("\n2️⃣ Test rotación individual")
try:
    engine.set_individual_rotation(5, speed_x=0.0, speed_y=1.0, speed_z=0.0)
    print("   ✅ Parámetros aceptados")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n✅ Test completado")
